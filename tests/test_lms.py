import os, tempfile, unittest
from datetime import date, timedelta
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from app import Database

class LMSTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Database(os.path.join(self.tmp.name,"test.db"))
        self.db.seed()

    def tearDown(self):
        self.tmp.cleanup()

    def test_valid_and_invalid_login(self):
        user,err=self.db.authenticate("admin","Admin@12345")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"],"Admin")
        self.assertIsNone(err)
        user,err=self.db.authenticate("admin","wrong")
        self.assertIsNone(user)
        self.assertIsNotNone(err)

    def test_borrow_and_return_are_consistent(self):
        member=self.db.members()[0]
        book=self.db.books()[0]
        before=book["available_copies"]
        self.db.borrow(member["id"],book["id"],(date.today()+timedelta(days=7)).isoformat())
        self.assertEqual(self.db.books()[0]["available_copies"],before-1)
        loan=self.db.loans(only_open=True)[0]
        self.db.return_loan(loan["id"])
        self.assertEqual(self.db.books()[0]["available_copies"],before)
        self.assertEqual(len(self.db.loans(only_open=True)),0)

    def test_cannot_delete_book_with_open_loan(self):
        member=self.db.members()[0]
        book=self.db.books()[0]
        self.db.borrow(member["id"],book["id"],(date.today()+timedelta(days=7)).isoformat())
        with self.assertRaises(ValueError):
            self.db.delete_book(book["id"])

    def test_search_title_author_category(self):
        self.assertTrue(self.db.books("Introduction","title"))
        self.assertTrue(self.db.books("Academic","author"))
        self.assertTrue(self.db.books("General","category"))

    def test_overdue_detection(self):
        member=self.db.members()[0]
        book=self.db.books()[0]
        with self.db.con() as con:
            con.execute(
                "INSERT INTO loans(book_id,member_id,borrow_date,due_date,status) VALUES(?,?,?,?, 'Open')",
                (book["id"],member["id"],(date.today()-timedelta(days=10)).isoformat(),(date.today()-timedelta(days=1)).isoformat())
            )
            con.execute("UPDATE books SET available_copies=available_copies-1 WHERE id=?",(book["id"],))
        self.assertEqual(len(self.db.loans(overdue=True)),1)

    def test_member_account_is_linked_to_own_member_record(self):
        user,_=self.db.authenticate("member","Member@12345")
        member=self.db.member_for_user(user["id"])
        self.assertIsNotNone(member)
        self.assertEqual(member["full_name"],"Demo Member")

if __name__=="__main__":
    unittest.main(verbosity=2)
