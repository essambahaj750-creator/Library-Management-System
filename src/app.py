from __future__ import annotations
import argparse, base64, hashlib, html, secrets, shutil, sqlite3, threading
from datetime import date, datetime, timedelta
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

APP_TITLE = "Library Management System"
SESSION_TIMEOUT_MINUTES = 30
MAX_FAILED_ATTEMPTS = 5
LOCK_MINUTES = 15

SCHEMA = r"""
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS roles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, salt TEXT NOT NULL,
 role_id INTEGER NOT NULL REFERENCES roles(id), active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
 failed_attempts INTEGER NOT NULL DEFAULT 0, locked_until TEXT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, description TEXT NULL);
CREATE TABLE IF NOT EXISTS members (
 id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, phone TEXT NOT NULL, registration_date TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Inactive')), user_id INTEGER NULL UNIQUE REFERENCES users(id));
CREATE TABLE IF NOT EXISTS books (
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT NOT NULL, category_id INTEGER NOT NULL REFERENCES categories(id),
 total_copies INTEGER NOT NULL CHECK(total_copies >= 0), available_copies INTEGER NOT NULL CHECK(available_copies >= 0 AND available_copies <= total_copies));
CREATE TABLE IF NOT EXISTS loans (
 id INTEGER PRIMARY KEY AUTOINCREMENT, book_id INTEGER NOT NULL REFERENCES books(id), member_id INTEGER NOT NULL REFERENCES members(id),
 borrow_date TEXT NOT NULL, due_date TEXT NOT NULL, return_date TEXT NULL, status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','Returned')));
CREATE INDEX IF NOT EXISTS idx_loans_status_due ON loans(status, due_date);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
"""

CSS = r"""
:root{--blue:#123b5d;--light:#eef5fb;--border:#c7d8e7;--danger:#9b1c1c;--ok:#236b2c}*{box-sizing:border-box}
body{margin:0;font-family:Segoe UI,Tahoma,Arial,sans-serif;background:#f7f9fb;color:#1f2d3d}header{background:var(--blue);color:white;padding:16px 28px;display:flex;justify-content:space-between;align-items:center}header h1{margin:0;font-size:22px}nav a{color:white;text-decoration:none;margin:0 8px;font-size:14px}main{max-width:1180px;margin:26px auto;padding:0 18px 40px}.card{background:white;border:1px solid var(--border);border-radius:12px;padding:18px;margin-bottom:18px;box-shadow:0 3px 12px rgba(0,0,0,.04)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.metric{font-size:30px;font-weight:700;color:var(--blue)}table{width:100%;border-collapse:collapse;background:white}th,td{border-bottom:1px solid #e7eef4;text-align:left;padding:10px;vertical-align:top}th{background:var(--light);color:var(--blue)}input,select,textarea{width:100%;padding:9px 10px;border:1px solid #b7c9d8;border-radius:7px;margin:4px 0 12px}button,.btn{display:inline-block;background:var(--blue);color:white;border:none;border-radius:7px;padding:9px 14px;cursor:pointer;text-decoration:none;margin:2px}.btn.secondary{background:#667788}.btn.danger{background:var(--danger)}.btn.ok{background:var(--ok)}.alert{padding:12px;border-radius:8px;background:#fff4cc;border:1px solid #ead27a;margin-bottom:14px}.error{color:var(--danger);font-weight:600}.ok{color:var(--ok);font-weight:600}form.inline{display:inline}.small{color:#6a7785;font-size:13px}.login{max-width:430px;margin:80px auto}.badge{border-radius:999px;padding:3px 9px;font-size:12px;background:#e8f2fa;color:var(--blue)}@media(max-width:800px){header{display:block}nav{margin-top:10px}th,td{font-size:12px;padding:7px}}
"""

def make_password(password, salt=None):
    salt_bytes=base64.b64decode(salt) if salt else secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt_bytes,120000)
    return base64.b64encode(digest).decode(),base64.b64encode(salt_bytes).decode()

def password_ok(password,password_hash,salt):
    candidate,_=make_password(password,salt)
    return secrets.compare_digest(candidate,password_hash)

class Database:
    def __init__(self,path):
        self.path=path
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        self.init()
    def con(self):
        con=sqlite3.connect(self.path,timeout=10)
        con.row_factory=sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con
    def init(self):
        with self.con() as con:
            con.executescript(SCHEMA)
            for role in ("Admin","Librarian","Member"):
                con.execute("INSERT OR IGNORE INTO roles(name) VALUES(?)",(role,))
    def role_id(self,con,role):
        row=con.execute("SELECT id FROM roles WHERE name=?",(role,)).fetchone()
        if not row:
            raise ValueError("Invalid role")
        return row["id"]
    def seed(self):
        with self.con() as con:
            if con.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]==0:
                for username,password,role in [
                    ("admin","Admin@12345","Admin"),
                    ("librarian","Lib@12345","Librarian"),
                    ("member","Member@12345","Member")
                ]:
                    h,s=make_password(password)
                    con.execute("INSERT INTO users(username,password_hash,salt,role_id) VALUES(?,?,?,?)",(username,h,s,self.role_id(con,role)))
                uid=con.execute("SELECT id FROM users WHERE username='member'").fetchone()["id"]
                con.execute("INSERT INTO members(full_name,phone,registration_date,status,user_id) VALUES(?,?,?,?,?)",("Demo Member","777000111",date.today().isoformat(),"Active",uid))
            con.execute("INSERT OR IGNORE INTO categories(name,description) VALUES('General','General collection')")
            cid=con.execute("SELECT id FROM categories WHERE name='General'").fetchone()["id"]
            if con.execute("SELECT COUNT(*) c FROM books").fetchone()["c"]==0:
                con.execute("INSERT INTO books(title,author,category_id,total_copies,available_copies) VALUES(?,?,?,?,?)",("Introduction to Computing","Academic Author",cid,3,3))
    def authenticate(self,username,password):
        with self.con() as con:
            row=con.execute("SELECT u.*,r.name role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.username=?",(username,)).fetchone()
            if not row:
                return None,"Invalid username or password."
            if not row["active"]:
                return None,"Account is inactive."
            if row["locked_until"]:
                until=datetime.fromisoformat(row["locked_until"])
                if until>datetime.now():
                    return None,f"Account locked until {until.strftime('%H:%M')}."
                con.execute("UPDATE users SET failed_attempts=0,locked_until=NULL WHERE id=?",(row["id"],))
            if not password_ok(password,row["password_hash"],row["salt"]):
                attempts=row["failed_attempts"]+1
                locked=None
                if attempts>=MAX_FAILED_ATTEMPTS:
                    locked=(datetime.now()+timedelta(minutes=LOCK_MINUTES)).replace(microsecond=0).isoformat(sep=" ")
                    attempts=0
                con.execute("UPDATE users SET failed_attempts=?,locked_until=? WHERE id=?",(attempts,locked,row["id"]))
                return None,"Invalid username or password."
            con.execute("UPDATE users SET failed_attempts=0,locked_until=NULL WHERE id=?",(row["id"],))
            return dict(row),None
    def create_user(self,username,password,role,active=1):
        if not username or len(password)<8:
            raise ValueError("Username and password (8+ chars) are required.")
        h,s=make_password(password)
        with self.con() as con:
            con.execute("INSERT INTO users(username,password_hash,salt,role_id,active) VALUES(?,?,?,?,?)",(username,h,s,self.role_id(con,role),1 if active else 0))
    def list_users(self):
        with self.con() as con:
            return con.execute("SELECT u.id,u.username,u.active,r.name role FROM users u JOIN roles r ON r.id=u.role_id ORDER BY u.username").fetchall()
    def toggle_user(self,user_id):
        with self.con() as con:
            con.execute("UPDATE users SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id=?",(user_id,))
    def set_role(self,user_id,role):
        with self.con() as con:
            con.execute("UPDATE users SET role_id=? WHERE id=?",(self.role_id(con,role),user_id))
    def add_category(self,name,description=""):
        if not name.strip():
            raise ValueError("Category name is required.")
        with self.con() as con:
            con.execute("INSERT INTO categories(name,description) VALUES(?,?)",(name.strip(),description.strip()))
    def categories(self):
        with self.con() as con:
            return con.execute("SELECT * FROM categories ORDER BY name").fetchall()
    def add_book(self,title,author,category_id,total_copies):
        total=int(total_copies)
        if not title.strip() or not author.strip() or total<0:
            raise ValueError("Valid book data is required.")
        with self.con() as con:
            con.execute("INSERT INTO books(title,author,category_id,total_copies,available_copies) VALUES(?,?,?,?,?)",(title.strip(),author.strip(),category_id,total,total))
    def update_book(self,bid,title,author,category_id,total_copies):
        total=int(total_copies)
        with self.con() as con:
            b=con.execute("SELECT * FROM books WHERE id=?",(bid,)).fetchone()
            if not b:
                raise ValueError("Book not found.")
            borrowed=b["total_copies"]-b["available_copies"]
            if total<borrowed:
                raise ValueError("Total copies cannot be less than currently borrowed copies.")
            con.execute("UPDATE books SET title=?,author=?,category_id=?,total_copies=?,available_copies=? WHERE id=?",(title.strip(),author.strip(),category_id,total,total-borrowed,bid))
    def delete_book(self,bid):
        with self.con() as con:
            if con.execute("SELECT COUNT(*) c FROM loans WHERE book_id=? AND return_date IS NULL",(bid,)).fetchone()["c"]:
                raise ValueError("Cannot delete a book with an open loan.")
            con.execute("DELETE FROM books WHERE id=?",(bid,))
    def books(self,q="",field="all"):
        with self.con() as con:
            sql="SELECT b.*,c.name category FROM books b JOIN categories c ON c.id=b.category_id"
            args=[]
            if q:
                like=f"%{q}%"
                if field=="title":
                    sql+=" WHERE b.title LIKE ?"; args=[like]
                elif field=="author":
                    sql+=" WHERE b.author LIKE ?"; args=[like]
                elif field=="category":
                    sql+=" WHERE c.name LIKE ?"; args=[like]
                else:
                    sql+=" WHERE b.title LIKE ? OR b.author LIKE ? OR c.name LIKE ?"; args=[like,like,like]
            return con.execute(sql+" ORDER BY b.title",args).fetchall()
    def add_member(self,full_name,phone,status="Active",user_id=None):
        if not full_name.strip() or not phone.strip():
            raise ValueError("Member name and phone are required.")
        with self.con() as con:
            con.execute("INSERT INTO members(full_name,phone,registration_date,status,user_id) VALUES(?,?,?,?,?)",(full_name.strip(),phone.strip(),date.today().isoformat(),status,user_id or None))
    def update_member(self,mid,full_name,phone,status):
        with self.con() as con:
            con.execute("UPDATE members SET full_name=?,phone=?,status=? WHERE id=?",(full_name.strip(),phone.strip(),status,mid))
    def members(self):
        with self.con() as con:
            return con.execute("SELECT * FROM members ORDER BY full_name").fetchall()
    def member_for_user(self,user_id):
        with self.con() as con:
            return con.execute("SELECT * FROM members WHERE user_id=?",(user_id,)).fetchone()
    def borrow(self,member_id,book_id,due_date):
        due=date.fromisoformat(due_date)
        if due<date.today():
            raise ValueError("Due date cannot be in the past.")
        con=self.con()
        try:
            con.execute("BEGIN IMMEDIATE")
            member=con.execute("SELECT * FROM members WHERE id=?",(member_id,)).fetchone()
            if not member or member["status"]!="Active":
                raise ValueError("Member must be registered and active.")
            book=con.execute("SELECT * FROM books WHERE id=?",(book_id,)).fetchone()
            if not book or book["available_copies"]<=0:
                raise ValueError("No available copy for this book.")
            con.execute("INSERT INTO loans(book_id,member_id,borrow_date,due_date,status) VALUES(?,?,?,?, 'Open')",(book_id,member_id,date.today().isoformat(),due.isoformat()))
            con.execute("UPDATE books SET available_copies=available_copies-1 WHERE id=? AND available_copies>0",(book_id,))
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
    def return_loan(self,loan_id):
        con=self.con()
        try:
            con.execute("BEGIN IMMEDIATE")
            loan=con.execute("SELECT * FROM loans WHERE id=?",(loan_id,)).fetchone()
            if not loan or loan["return_date"] is not None:
                raise ValueError("Loan is not open.")
            con.execute("UPDATE loans SET return_date=?,status='Returned' WHERE id=?",(date.today().isoformat(),loan_id))
            con.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?",(loan["book_id"],))
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
    def loans(self,member_id=None,only_open=False,overdue=False):
        with self.con() as con:
            sql="""SELECT l.*,b.title book,m.full_name member,
                   CASE WHEN l.return_date IS NULL AND date(l.due_date)<date('now','localtime') THEN 1 ELSE 0 END overdue
                   FROM loans l JOIN books b ON b.id=l.book_id JOIN members m ON m.id=l.member_id WHERE 1=1"""
            args=[]
            if member_id is not None:
                sql+=" AND l.member_id=?"; args.append(member_id)
            if only_open:
                sql+=" AND l.return_date IS NULL"
            if overdue:
                sql+=" AND l.return_date IS NULL AND date(l.due_date)<date('now','localtime')"
            return con.execute(sql+" ORDER BY l.id DESC",args).fetchall()
    def counts(self):
        with self.con() as con:
            return {
                "books":con.execute("SELECT COUNT(*) c FROM books").fetchone()["c"],
                "members":con.execute("SELECT COUNT(*) c FROM members").fetchone()["c"],
                "open":con.execute("SELECT COUNT(*) c FROM loans WHERE return_date IS NULL").fetchone()["c"],
                "overdue":con.execute("SELECT COUNT(*) c FROM loans WHERE return_date IS NULL AND date(due_date)<date('now','localtime')").fetchone()["c"]
            }

SESSIONS={}
SESSIONS_LOCK=threading.Lock()

def esc(x):
    return html.escape(str(x) if x is not None else "")

def nav(user):
    if not user:
        return ""
    links=[("Dashboard","/dashboard"),("Books","/books")]
    if user["role"]=="Member":
        links += [("My Profile","/my/profile"),("My Loans","/my/loans")]
    if user["role"] in ("Admin","Librarian"):
        links += [("Categories","/categories"),("Members","/members"),("Loans","/loans"),("Borrow","/borrow"),("Overdue","/overdue")]
    if user["role"]=="Admin":
        links += [("Users","/users")]
    links += [("Logout","/logout")]
    return "".join(f'<a href="{u}">{esc(t)}</a>' for t,u in links)

def page(title,body,user=None):
    who=f'{esc(user["username"])} · {esc(user["role"])}' if user else ""
    return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{esc(title)} — {APP_TITLE}</title><style>{CSS}</style></head><body><header><h1>{APP_TITLE}</h1><div>{nav(user)} <span class='small' style='color:#d9e8f5'>{who}</span></div></header><main>{body}</main></body></html>"

def fv(d,k,default=""):
    return d.get(k,[default])[0]

class LMSHandler(BaseHTTPRequestHandler):
    db=None
    server_version="LMS/1.0"
    def log_message(self,format,*args):
        print("[HTTP]",format%args)
    def body_params(self):
        n=int(self.headers.get("Content-Length","0") or 0)
        return parse_qs(self.rfile.read(n).decode("utf-8") if n else "",keep_blank_values=True)
    def cookies(self):
        c=SimpleCookie(); c.load(self.headers.get("Cookie","")); return c
    def current_user(self):
        sid=self.cookies().get("sid")
        if not sid:
            return None
        with SESSIONS_LOCK:
            sess=SESSIONS.get(sid.value)
            if not sess:
                return None
            if datetime.now()-sess["last"]>timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                SESSIONS.pop(sid.value,None)
                return None
            sess["last"]=datetime.now()
            return sess["user"]
    def send_html(self,content,status=200,cookie=None):
        data=content.encode()
        self.send_response(status)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Cache-Control","no-store")
        if cookie:
            self.send_header("Set-Cookie",cookie)
        self.end_headers()
        self.wfile.write(data)
    def redirect(self,location,cookie=None):
        self.send_response(303)
        self.send_header("Location",location)
        if cookie:
            self.send_header("Set-Cookie",cookie)
        self.end_headers()
    def require(self,roles=None):
        u=self.current_user()
        if not u:
            self.redirect("/login")
            return None
        if roles and u["role"] not in roles:
            self.send_html(page("Forbidden","<div class='card'><h2>Access denied</h2><p>You do not have permission to access this function.</p></div>",u),403)
            return None
        return u
    def do_GET(self):
        parsed=urlparse(self.path)
        path=parsed.path
        q=parse_qs(parsed.query)
        if path in ("/","/login"):
            if self.current_user():
                return self.redirect("/dashboard")
            return self.send_html(page("Login","<div class='card login'><h2>Sign in</h2><form method='post' action='/login'><label>Username</label><input name='username' required><label>Password</label><input type='password' name='password' required><button>Sign in</button></form><p class='small'>Demo: admin / Admin@12345</p></div>"))
        if path=="/logout":
            sid=self.cookies().get("sid")
            if sid:
                with SESSIONS_LOCK:
                    SESSIONS.pop(sid.value,None)
            return self.redirect("/login","sid=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")
        if path=="/dashboard":
            u=self.require()
            if not u:
                return
            c=self.db.counts()
            body="<h2>Dashboard</h2><div class='grid'>"+"".join(f"<div class='card'><div class='metric'>{v}</div><div>{k}</div></div>" for k,v in [("Books",c['books']),("Members",c['members']),("Open loans",c['open']),("Overdue",c['overdue'])])+"</div>"
            return self.send_html(page("Dashboard",body,u))
        if path=="/books":
            u=self.require()
            if not u:
                return
            search=fv(q,"q","")
            field=fv(q,"field","all")
            rows=self.db.books(search,field)
            add="<a class='btn' href='/books/new'>Add book</a>" if u["role"] in ("Admin","Librarian") else ""
            body=f"<h2>Books</h2><div class='card'><form method='get'><input name='q' value='{esc(search)}' placeholder='Search title, author, category'><select name='field'><option value='all'>All</option><option value='title'>Title</option><option value='author'>Author</option><option value='category'>Category</option></select><button>Search</button> {add}</form></div><div class='card'><table><tr><th>Title</th><th>Author</th><th>Category</th><th>Total</th><th>Available</th><th>State</th>"+("<th>Actions</th>" if u['role'] in ('Admin','Librarian') else "")+"</tr>"
            for r in rows:
                body+=f"<tr><td>{esc(r['title'])}</td><td>{esc(r['author'])}</td><td>{esc(r['category'])}</td><td>{r['total_copies']}</td><td>{r['available_copies']}</td><td><span class='badge'>{'Available' if r['available_copies']>0 else 'Unavailable'}</span></td>"
                if u["role"] in ("Admin","Librarian"):
                    body+=f"<td><a class='btn secondary' href='/books/edit?id={r['id']}'>Edit</a><form class='inline' method='post' action='/books/delete'><input type='hidden' name='id' value='{r['id']}'><button class='btn danger'>Delete</button></form></td>"
                body+="</tr>"
            return self.send_html(page("Books",body+"</table></div>",u))
        if path=="/books/new":
            u=self.require(("Admin","Librarian"))
            if not u:
                return
            opts="".join(f"<option value='{c['id']}'>{esc(c['name'])}</option>" for c in self.db.categories())
            body=f"<div class='card'><h2>Add Book</h2><form method='post'><label>Title</label><input name='title' required><label>Author</label><input name='author' required><label>Category</label><select name='category_id'>{opts}</select><label>Total copies</label><input type='number' min='0' name='total_copies' value='1' required><button>Add</button></form></div>"
            return self.send_html(page("Add Book",body,u))
        if path=="/books/edit":
            u=self.require(("Admin","Librarian"))
            if not u:
                return
            bid=int(fv(q,"id","0"))
            b=next((r for r in self.db.books() if r['id']==bid),None)
            if not b:
                return self.send_html(page("Not found","<div class='card'>Book not found.</div>",u),404)
            opts="".join(f"<option value='{c['id']}' {'selected' if c['id']==b['category_id'] else ''}>{esc(c['name'])}</option>" for c in self.db.categories())
            body=f"<div class='card'><h2>Edit Book</h2><form method='post'><input type='hidden' name='id' value='{bid}'><label>Title</label><input name='title' value='{esc(b['title'])}' required><label>Author</label><input name='author' value='{esc(b['author'])}' required><label>Category</label><select name='category_id'>{opts}</select><label>Total copies</label><input type='number' min='0' name='total_copies' value='{b['total_copies']}' required><button>Save</button></form></div>"
            return self.send_html(page("Edit Book",body,u))
        if path=="/categories":
            u=self.require(("Admin","Librarian"))
            if not u:
                return
            body="<h2>Categories</h2><div class='card'><form method='post' action='/categories/new'><label>Name</label><input name='name' required><label>Description</label><input name='description'><button>Add category</button></form></div><div class='card'><table><tr><th>Name</th><th>Description</th></tr>"+"".join(f"<tr><td>{esc(r['name'])}</td><td>{esc(r['description'])}</td></tr>" for r in self.db.categories())+"</table><p class='small'>Category deletion is intentionally out of scope.</p></div>"
            return self.send_html(page("Categories",body,u))
        if path=="/members":
            u=self.require(("Admin","Librarian"))
            if not u:
                return
            body="<h2>Members</h2><a class='btn' href='/members/new'>Register member</a><div class='card'><table><tr><th>Name</th><th>Phone</th><th>Registered</th><th>Status</th><th>Actions</th></tr>"+"".join(f"<tr><td>{esc(r['full_name'])}</td><td>{esc(r['phone'])}</td><td>{r['registration_date']}</td><td>{r['status']}</td><td><a class='btn secondary' href='/members/edit?id={r['id']}'>Edit</a></td></tr>" for r in self.db.members())+"</table></div>"
            return self.send_html(page("Members",body,u))
        if path=="/members/new":
            u=self.require(("Admin","Librarian"))
            if not u:
                return
            return self.send_html(page("Register Member","<div class='card'><h2>Register Member</h2><form method='post'><label>Full name</label><input name='full_name' required><label>Phone</label><input name='phone' required><label>Status</label><select name='status'><option>Active</option><option>Inactive</option></select><button>Register</button></form></div>",u))
        if path=="/members/edit":
            u=self.require(("Admin","Librarian"))
            if not u:
                return
            mid=int(fv(q,"id","0"))
            m=next((x for x in self.db.members() if x['id']==mid),None)
            if not m:
                return self.send_html(page("Not found","<div class='card'>Member not found.</div>",u),404)
            body=f"<div class='card'><h2>Edit Member</h2><form method='post'><input type='hidden' name='id' value='{mid}'><label>Full name</label><input name='full_name' value='{esc(m['full_name'])}' required><label>Phone</label><input name='phone' value='{esc(m['phone'])}' required><label>Status</label><select name='status'><option {'selected' if m['status']=='Active' else ''}>Active</option><option {'selected' if m['status']=='Inactive' else ''}>Inactive</option></select><button>Save</button></form></div>"
            return self.send_html(page("Edit Member",body,u))
        if path=="/borrow":
            u=self.require(("Admin","Librarian"))
            if not u:
                return
            mo="".join(f"<option value='{x['id']}'>{esc(x['full_name'])}</option>" for x in self.db.members() if x['status']=='Active')
            bo="".join(f"<option value='{x['id']}'>{esc(x['title'])} ({x['available_copies']} available)</option>" for x in self.db.books() if x['available_copies']>0)
            due=(date.today()+timedelta(days=14)).isoformat()
            body=f"<div class='card'><h2>Borrow Book</h2><form method='post'><label>Member</label><select name='member_id'>{mo}</select><label>Book</label><select name='book_id'>{bo}</select><label>Due date</label><input type='date' name='due_date' value='{due}' required><button>Register borrowing</button></form></div>"
            return self.send_html(page("Borrow",body,u))
        if path=="/loans":
            u=self.require(("Admin","Librarian"))
            if not u:
                return
            body="<h2>Current Loans</h2><div class='card'><table><tr><th>Book</th><th>Member</th><th>Borrowed</th><th>Due</th><th>Status</th><th>Action</th></tr>"
            for r in self.db.loans(only_open=True):
                body+=f"<tr><td>{esc(r['book'])}</td><td>{esc(r['member'])}</td><td>{r['borrow_date']}</td><td>{r['due_date']}</td><td>{'<span class=error>Overdue</span>' if r['overdue'] else 'Open'}</td><td><form method='post' action='/return'><input type='hidden' name='loan_id' value='{r['id']}'><button class='btn ok'>Return</button></form></td></tr>"
            return self.send_html(page("Loans",body+"</table></div>",u))
        if path=="/overdue":
            u=self.require(("Admin","Librarian"))
            if not u:
                return
            rows=self.db.loans(overdue=True)
            body="<h2>Overdue Loans</h2><div class='card'><table><tr><th>Book</th><th>Member</th><th>Due date</th></tr>"+"".join(f"<tr><td>{esc(r['book'])}</td><td>{esc(r['member'])}</td><td>{r['due_date']}</td></tr>" for r in rows)+"</table></div>"
            return self.send_html(page("Overdue",body,u))
        if path=="/my/profile":
            u=self.require(("Member",))
            if not u:
                return
            m=self.db.member_for_user(u['id'])
            body=f"<h2>My Profile</h2><div class='card'><p><b>Name:</b> {esc(m['full_name'] if m else '')}</p><p><b>Phone:</b> {esc(m['phone'] if m else '')}</p><p><b>Status:</b> {esc(m['status'] if m else '')}</p></div>"
            return self.send_html(page("My Profile",body,u))
        if path=="/my/loans":
            u=self.require(("Member",))
            if not u:
                return
            m=self.db.member_for_user(u['id'])
            rows=self.db.loans(m['id'] if m else -1)
            body="<h2>My Loans</h2><div class='card'><table><tr><th>Book</th><th>Borrow date</th><th>Due date</th><th>Return date</th><th>Status</th></tr>"+"".join(f"<tr><td>{esc(r['book'])}</td><td>{r['borrow_date']}</td><td>{r['due_date']}</td><td>{esc(r['return_date'])}</td><td>{'<span class=error>Overdue</span>' if r['overdue'] else esc(r['status'])}</td></tr>" for r in rows)+"</table></div>"
            return self.send_html(page("My Loans",body,u))
        if path=="/users":
            u=self.require(("Admin",))
            if not u:
                return
            body="<h2>User Accounts</h2><div class='card'><h3>Create account</h3><form method='post' action='/users/new'><label>Username</label><input name='username' required><label>Password</label><input type='password' name='password' minlength='8' required><label>Role</label><select name='role'><option>Admin</option><option>Librarian</option><option>Member</option></select><button>Create</button></form></div><div class='card'><table><tr><th>Username</th><th>Role</th><th>Active</th><th>Actions</th></tr>"
            for r in self.db.list_users():
                body+=f"<tr><td>{esc(r['username'])}</td><td>{esc(r['role'])}</td><td>{'Yes' if r['active'] else 'No'}</td><td><form class='inline' method='post' action='/users/toggle'><input type='hidden' name='id' value='{r['id']}'><button class='btn secondary'>Toggle active</button></form><form class='inline' method='post' action='/users/role'><input type='hidden' name='id' value='{r['id']}'><select name='role' style='width:auto;display:inline'><option>Admin</option><option>Librarian</option><option>Member</option></select><button>Set role</button></form></td></tr>"
            return self.send_html(page("Users",body+"</table></div>",u))
        self.send_html(page("Not Found","<div class='card'>Page not found.</div>",self.current_user()),404)
    def do_POST(self):
        path=urlparse(self.path).path
        d=self.body_params()
        try:
            if path=="/login":
                user,err=self.db.authenticate(fv(d,"username"),fv(d,"password"))
                if err:
                    return self.send_html(page("Login",f"<div class='card login'><h2>Sign in</h2><p class='error'>{esc(err)}</p><form method='post'><input name='username' required><input type='password' name='password' required><button>Sign in</button></form></div>"),401)
                token=secrets.token_urlsafe(32)
                with SESSIONS_LOCK:
                    SESSIONS[token]={"user":user,"last":datetime.now()}
                return self.redirect("/dashboard",f"sid={token}; Path=/; HttpOnly; SameSite=Lax")
            rules={
                "/books/new":(("Admin","Librarian"),lambda:self.db.add_book(fv(d,"title"),fv(d,"author"),int(fv(d,"category_id")),int(fv(d,"total_copies"))),"/books"),
                "/books/edit":(("Admin","Librarian"),lambda:self.db.update_book(int(fv(d,"id")),fv(d,"title"),fv(d,"author"),int(fv(d,"category_id")),int(fv(d,"total_copies"))),"/books"),
                "/books/delete":(("Admin","Librarian"),lambda:self.db.delete_book(int(fv(d,"id"))),"/books"),
                "/categories/new":(("Admin","Librarian"),lambda:self.db.add_category(fv(d,"name"),fv(d,"description")),"/categories"),
                "/members/new":(("Admin","Librarian"),lambda:self.db.add_member(fv(d,"full_name"),fv(d,"phone"),fv(d,"status","Active")),"/members"),
                "/members/edit":(("Admin","Librarian"),lambda:self.db.update_member(int(fv(d,"id")),fv(d,"full_name"),fv(d,"phone"),fv(d,"status")),"/members"),
                "/borrow":(("Admin","Librarian"),lambda:self.db.borrow(int(fv(d,"member_id")),int(fv(d,"book_id")),fv(d,"due_date")),"/loans"),
                "/return":(("Admin","Librarian"),lambda:self.db.return_loan(int(fv(d,"loan_id"))),"/loans"),
                "/users/new":(("Admin",),lambda:self.db.create_user(fv(d,"username"),fv(d,"password"),fv(d,"role")),"/users"),
                "/users/toggle":(("Admin",),lambda:self.db.toggle_user(int(fv(d,"id"))),"/users"),
                "/users/role":(("Admin",),lambda:self.db.set_role(int(fv(d,"id")),fv(d,"role")),"/users")
            }
            if path in rules:
                roles,fn,target=rules[path]
                u=self.require(roles)
                if not u:
                    return
                fn()
                return self.redirect(target)
            return self.send_html(page("Not Found","<div class='card'>Unknown action.</div>",self.current_user()),404)
        except (ValueError,sqlite3.IntegrityError) as ex:
            return self.send_html(page("Validation Error",f"<div class='card'><h2>Operation rejected</h2><p class='error'>{esc(ex)}</p><a class='btn' href='javascript:history.back()'>Back</a></div>",self.current_user()),400)

def backup_database(db_path,backup_dir):
    source=Path(db_path)
    target_dir=Path(backup_dir)
    target_dir.mkdir(parents=True,exist_ok=True)
    target=target_dir/f"lms_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    src=sqlite3.connect(source)
    dst=sqlite3.connect(target)
    with dst:
        src.backup(dst)
    src.close()
    dst.close()
    for old in sorted(target_dir.glob("lms_backup_*.db"),reverse=True)[7:]:
        old.unlink(missing_ok=True)
    return target

def restore_database(backup_path,db_path):
    src=Path(backup_path)
    dst=Path(db_path)
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)

def main():
    ap=argparse.ArgumentParser(description=APP_TITLE)
    ap.add_argument("--db",default=str(Path(__file__).with_name("data").joinpath("lms.db")))
    ap.add_argument("--host",default="127.0.0.1")
    ap.add_argument("--port",type=int,default=8080)
    ap.add_argument("--backup",action="store_true")
    ap.add_argument("--restore")
    args=ap.parse_args()
    db=Database(args.db)
    db.seed()
    if args.backup:
        print(backup_database(args.db,str(Path(args.db).parent/"backups")))
        return
    if args.restore:
        restore_database(args.restore,args.db)
        print("Restored.")
        return
    LMSHandler.db=db
    print(f"LMS running at http://{args.host}:{args.port}")
    print("Demo accounts: admin/Admin@12345, librarian/Lib@12345, member/Member@12345")
    ThreadingHTTPServer((args.host,args.port),LMSHandler).serve_forever()

if __name__=="__main__":
    main()
