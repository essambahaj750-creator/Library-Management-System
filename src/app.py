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
:root{
  --navy:#0b1f33;
  --navy-2:#102a43;
  --blue:#2563eb;
  --blue-2:#3b82f6;
  --cyan:#06b6d4;
  --green:#16a34a;
  --red:#dc2626;
  --amber:#d97706;
  --bg:#f4f7fb;
  --surface:#ffffff;
  --surface-2:#f8fafc;
  --text:#172033;
  --muted:#697386;
  --border:#e2e8f0;
  --shadow:0 10px 30px rgba(15,23,42,.07);
  --shadow-lg:0 22px 60px rgba(15,23,42,.13);
  --radius:18px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;
  min-height:100vh;
  font-family:"Segoe UI",Tahoma,Arial,sans-serif;
  background:var(--bg);
  color:var(--text);
  -webkit-font-smoothing:antialiased;
}
a{color:inherit}
.app-shell{min-height:100vh;display:flex}
.sidebar{
  width:270px;
  position:fixed;
  inset:0 auto 0 0;
  background:linear-gradient(180deg,#0b1f33 0%,#102a43 100%);
  color:#fff;
  padding:26px 18px 20px;
  box-shadow:12px 0 40px rgba(15,23,42,.12);
  z-index:30;
  overflow-y:auto;
}
.brand{
  display:flex;
  align-items:center;
  gap:13px;
  padding:2px 8px 22px;
  border-bottom:1px solid rgba(255,255,255,.10);
  margin-bottom:18px;
}
.brand-mark{
  width:46px;height:46px;border-radius:14px;
  display:grid;place-items:center;
  background:linear-gradient(135deg,#3b82f6,#06b6d4);
  box-shadow:0 10px 25px rgba(59,130,246,.28);
  font-size:24px;
}
.brand-title{font-size:17px;font-weight:800;line-height:1.15}
.brand-sub{font-size:11px;color:#a9bdd0;margin-top:4px;letter-spacing:.4px}
.user-card{
  padding:13px 14px;
  border-radius:14px;
  background:rgba(255,255,255,.07);
  border:1px solid rgba(255,255,255,.08);
  margin:0 4px 18px;
}
.user-name{font-weight:700;font-size:14px}
.user-role{font-size:12px;color:#b9cce0;margin-top:3px}
.side-nav{display:flex;flex-direction:column;gap:5px}
.side-nav a{
  display:flex;align-items:center;gap:11px;
  text-decoration:none;color:#d7e4f0;
  padding:11px 12px;border-radius:11px;
  font-size:14px;font-weight:600;
  transition:.18s ease;
}
.side-nav a:hover{
  background:rgba(59,130,246,.20);
  color:#fff;
  transform:translateX(3px);
}
.side-nav a.logout{
  margin-top:12px;
  color:#fecaca;
  border-top:1px solid rgba(255,255,255,.08);
  border-radius:0;
  padding-top:17px;
}
.nav-icon{width:24px;text-align:center;font-size:16px}
.sidebar-foot{
  margin:22px 8px 0;
  padding-top:16px;
  border-top:1px solid rgba(255,255,255,.08);
  font-size:11px;color:#829bb3;
}
.workspace{margin-left:270px;min-width:0;width:calc(100% - 270px)}
.topbar{
  height:76px;background:rgba(255,255,255,.92);
  backdrop-filter:blur(14px);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  padding:0 34px;
  position:sticky;top:0;z-index:20;
}
.topbar h1{font-size:20px;margin:0;color:#0f172a}
.topbar-meta{font-size:12px;color:var(--muted)}
main{max-width:1320px;margin:0 auto;padding:34px 32px 50px}
.page-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-end;margin-bottom:22px}
.page-head h2{margin:0;font-size:28px;letter-spacing:-.4px;color:#0f172a}
.page-head p{margin:7px 0 0;color:var(--muted)}
.hero{
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,#0f2f4a 0%,#164e73 52%,#2563eb 100%);
  color:#fff;border-radius:24px;padding:30px 32px;margin-bottom:24px;
  box-shadow:0 18px 44px rgba(37,99,235,.18);
}
.hero:after{
  content:"";position:absolute;width:280px;height:280px;border-radius:50%;
  background:rgba(255,255,255,.08);right:-80px;top:-110px;
}
.hero h2{margin:0;font-size:29px;letter-spacing:-.5px}
.hero p{margin:8px 0 0;color:#d9ecff;max-width:700px;line-height:1.6}
.hero-badge{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.16);
  border-radius:999px;padding:6px 10px;font-size:12px;margin-bottom:13px;
}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-bottom:24px}
.stat-card{
  background:#fff;border:1px solid var(--border);border-radius:18px;
  padding:19px;box-shadow:var(--shadow);
  display:flex;justify-content:space-between;align-items:center;gap:14px;
}
.stat-icon{
  width:48px;height:48px;border-radius:14px;display:grid;place-items:center;
  background:#eff6ff;color:#2563eb;font-size:21px;
}
.stat-card.danger .stat-icon{background:#fef2f2;color:#dc2626}
.stat-card.success .stat-icon{background:#f0fdf4;color:#16a34a}
.stat-card.cyan .stat-icon{background:#ecfeff;color:#0891b2}
.metric{font-size:30px;font-weight:800;color:#0f172a;line-height:1}
.metric-label{font-size:13px;color:var(--muted);margin-top:6px}
.card{
  background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  padding:22px;margin-bottom:20px;box-shadow:var(--shadow);
}
.card h2,.card h3{margin-top:0;color:#0f172a}
.card h3{font-size:17px}
.card-head{
  display:flex;align-items:center;justify-content:space-between;gap:16px;
  margin-bottom:16px;
}
.quick-actions{display:flex;gap:10px;flex-wrap:wrap}
.panel{
  background:var(--surface-2);border:1px solid var(--border);
  border-radius:16px;padding:17px;
}
table{
  width:100%;border-collapse:separate;border-spacing:0;
  background:#fff;border:1px solid var(--border);border-radius:14px;
  overflow:hidden;
}
th,td{
  border-bottom:1px solid #edf1f5;text-align:left;
  padding:12px 13px;vertical-align:middle;font-size:13px;
}
th{
  background:#f8fafc;color:#475569;font-size:12px;
  text-transform:uppercase;letter-spacing:.3px;font-weight:800;
}
tr:last-child td{border-bottom:0}
tbody tr:hover td{background:#f8fbff}
label{display:block;font-size:13px;font-weight:700;color:#334155;margin-bottom:5px}
input,select,textarea{
  width:100%;padding:11px 12px;border:1px solid #cbd5e1;border-radius:11px;
  margin:3px 0 14px;background:#fff;color:#172033;font-size:14px;
  transition:border-color .18s,box-shadow .18s;
}
input:focus,select:focus,textarea:focus{
  outline:none;border-color:#3b82f6;
  box-shadow:0 0 0 4px rgba(59,130,246,.12);
}
button,.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:7px;
  background:linear-gradient(135deg,#2563eb,#1d4ed8);color:white;
  border:0;border-radius:10px;padding:10px 14px;cursor:pointer;
  text-decoration:none;font-size:13px;font-weight:700;margin:2px;
  box-shadow:0 7px 16px rgba(37,99,235,.16);
  transition:.16s ease;
}
button:hover,.btn:hover{transform:translateY(-1px);filter:brightness(1.04)}
.btn.secondary{background:#64748b;box-shadow:none}
.btn.danger{background:#dc2626;box-shadow:none}
.btn.ok{background:#16a34a;box-shadow:none}
.alert{
  padding:13px 15px;border-radius:12px;background:#fff8e7;
  border:1px solid #f2d98a;color:#7c5b00;margin-bottom:15px;
}
.error{color:var(--red);font-weight:700}
.ok{color:var(--green);font-weight:700}
form.inline{display:inline}
.small{color:var(--muted);font-size:12px}
.badge{
  display:inline-flex;align-items:center;border-radius:999px;
  padding:5px 9px;font-size:11px;font-weight:800;
  background:#eaf2ff;color:#1d4ed8;
}
.badge.ok{background:#ecfdf3;color:#15803d}
.badge.warn{background:#fff7ed;color:#c2410c}
.badge.danger{background:#fef2f2;color:#b91c1c}
.empty{padding:35px;text-align:center;color:var(--muted)}
.footer{
  text-align:center;color:#94a3b8;font-size:11px;padding:0 20px 28px;
}
.login-wrap{
  min-height:100vh;display:grid;grid-template-columns:1.05fr .95fr;
  background:#f8fafc;
}
.login-visual{
  position:relative;overflow:hidden;
  background:linear-gradient(145deg,#071a2b 0%,#0f3655 50%,#2563eb 100%);
  color:#fff;padding:70px;display:flex;flex-direction:column;justify-content:center;
}
.login-visual:before,.login-visual:after{
  content:"";position:absolute;border-radius:50%;background:rgba(255,255,255,.06)
}
.login-visual:before{width:360px;height:360px;right:-120px;top:-90px}
.login-visual:after{width:220px;height:220px;left:-80px;bottom:-70px}
.login-logo{
  width:70px;height:70px;border-radius:20px;background:rgba(255,255,255,.12);
  border:1px solid rgba(255,255,255,.18);display:grid;place-items:center;
  font-size:34px;margin-bottom:22px;box-shadow:0 18px 40px rgba(0,0,0,.16);
}
.login-visual h1{font-size:38px;margin:0 0 12px;letter-spacing:-.8px}
.login-visual p{font-size:16px;line-height:1.75;color:#d5e7f7;max-width:530px}
.feature-list{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-top:26px;max-width:560px}
.feature-item{
  background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.10);
  padding:11px 12px;border-radius:12px;font-size:13px;color:#e7f2fb;
}
.login-panel{
  display:flex;align-items:center;justify-content:center;padding:42px;
  background:#fff;
}
.login-card{width:100%;max-width:430px}
.login-card .eyebrow{
  color:#2563eb;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:1px
}
.login-card h2{font-size:31px;margin:8px 0 6px;color:#0f172a}
.login-card .intro{color:var(--muted);margin:0 0 27px;line-height:1.6}
.login-card button{width:100%;padding:12px 16px;margin-top:4px}
.demo-box{
  margin-top:20px;padding:13px;border:1px dashed #bfdbfe;
  background:#eff6ff;border-radius:12px;color:#3b4c68;font-size:12px;line-height:1.7;
}
@media(max-width:1100px){
  .stats-grid{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:900px){
  .sidebar{width:82px;padding:22px 10px}
  .brand-title,.brand-sub,.user-card,.side-nav .nav-text,.sidebar-foot{display:none}
  .brand{justify-content:center;padding:0 0 18px}
  .brand-mark{width:46px;height:46px}
  .side-nav a{justify-content:center;padding:12px 8px}
  .nav-icon{font-size:18px}
  .workspace{margin-left:82px;width:calc(100% - 82px)}
  .topbar{padding:0 20px}
  main{padding:25px 18px 40px}
  .login-wrap{grid-template-columns:1fr}
  .login-visual{display:none}
}
@media(max-width:620px){
  .stats-grid{grid-template-columns:1fr}
  .page-head{display:block}
  .topbar h1{font-size:16px}
  .topbar-meta{display:none}
  .card{padding:16px}
  th,td{font-size:11px;padding:9px 8px}
  .login-panel{padding:28px 20px}
}

/* Premium refinement */
:root{
  --purple:#7c3aed;
  --soft-blue:#f4f8ff;
  --soft-purple:#f7f3ff;
}
svg.icon{width:19px;height:19px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;display:block}
.brand-mark svg{width:27px;height:27px;stroke:white}
.nav-icon{display:grid;place-items:center}
.nav-icon svg{width:18px;height:18px}
.topbar{
  box-shadow:0 1px 0 rgba(15,23,42,.02);
}
.topbar-left{display:flex;align-items:center;gap:14px}
.topbar-title small{display:block;margin-top:3px;color:#94a3b8;font-size:11px;font-weight:500}
.topbar-search{
  min-width:290px;max-width:380px;width:34vw;
  display:flex;align-items:center;gap:9px;
  background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;
  padding:7px 10px;
}
.topbar-search input{
  border:0;box-shadow:none;margin:0;padding:4px 2px;background:transparent;font-size:13px;
}
.topbar-search input:focus{box-shadow:none}
.topbar-search button{
  margin:0;padding:6px 9px;border-radius:8px;box-shadow:none;font-size:12px;
}
.section-grid{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(300px,.75fr);gap:20px}
.activity-list{display:flex;flex-direction:column;gap:10px}
.activity-item{
  display:grid;grid-template-columns:42px 1fr auto;align-items:center;gap:12px;
  padding:12px;border:1px solid #eef2f7;border-radius:14px;background:#fff;
}
.activity-dot{
  width:42px;height:42px;border-radius:12px;display:grid;place-items:center;
  background:#eff6ff;color:#2563eb;
}
.activity-dot svg{width:18px;height:18px}
.activity-title{font-weight:700;font-size:13px;color:#1e293b}
.activity-sub{font-size:11px;color:#94a3b8;margin-top:3px}
.activity-time{font-size:11px;color:#94a3b8;white-space:nowrap}
.insight-card{
  position:relative;overflow:hidden;
  background:linear-gradient(145deg,#111c2d,#173b5e);
  color:white;border:0;
}
.insight-card:after{
  content:"";position:absolute;right:-60px;bottom:-80px;width:190px;height:190px;
  border-radius:50%;background:rgba(59,130,246,.18);
}
.insight-card h3{color:white;position:relative;z-index:1}
.insight-card p{color:#c8d9e8;line-height:1.6;position:relative;z-index:1}
.insight-mini{
  display:flex;align-items:center;justify-content:space-between;
  padding:11px 0;border-bottom:1px solid rgba(255,255,255,.09);position:relative;z-index:1;
}
.insight-mini:last-child{border-bottom:0}
.insight-mini span{color:#b9cce0;font-size:12px}
.insight-mini strong{font-size:13px}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 16px}
.form-grid .full{grid-column:1/-1}
.data-card{padding:0;overflow:hidden}
.data-card .card-head{padding:20px 20px 0}
.data-card .table-wrap{overflow-x:auto;padding:0 20px 20px}
.table-wrap table{min-width:720px}
.profile-grid{display:grid;grid-template-columns:220px 1fr;gap:20px}
.profile-card{
  background:linear-gradient(160deg,#f8fbff,#eef5ff);
  border:1px solid #dbeafe;border-radius:18px;padding:22px;text-align:center;
}
.avatar{
  width:82px;height:82px;margin:0 auto 14px;border-radius:24px;
  display:grid;place-items:center;
  background:linear-gradient(135deg,#2563eb,#7c3aed);color:#fff;
  font-size:29px;font-weight:800;box-shadow:0 14px 30px rgba(37,99,235,.22);
}
.profile-name{font-size:18px;font-weight:800;color:#0f172a}
.profile-role{font-size:12px;color:#64748b;margin-top:4px}
.profile-details{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.detail-box{
  background:#fff;border:1px solid #e7edf5;border-radius:14px;padding:14px;
}
.detail-label{font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:.4px}
.detail-value{font-size:14px;font-weight:700;color:#1e293b;margin-top:5px}
.kpi-strip{
  display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:18px;
}
.kpi{
  padding:13px;border-radius:14px;background:#fff;border:1px solid #e7edf5;
}
.kpi strong{display:block;font-size:20px;color:#0f172a}
.kpi span{font-size:11px;color:#94a3b8}
.login-visual{
  background:
    radial-gradient(circle at 72% 20%,rgba(96,165,250,.24),transparent 28%),
    radial-gradient(circle at 18% 82%,rgba(124,58,237,.18),transparent 25%),
    linear-gradient(145deg,#071723 0%,#0b2942 45%,#164e73 72%,#2563eb 100%);
}
.login-card{
  padding:10px;
}
.demo-accounts{display:grid;grid-template-columns:1fr;gap:8px;margin-top:18px}
.demo-account{
  display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:10px 11px;border:1px solid #e2e8f0;border-radius:11px;background:#f8fafc;
}
.demo-account b{font-size:12px;color:#334155}
.demo-account code{font-size:11px;color:#64748b}
.soft-chip{
  display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border-radius:999px;
  background:#f1f5f9;color:#475569;font-size:11px;font-weight:700;
}
.member-hero{
  background:
    radial-gradient(circle at 85% 30%,rgba(255,255,255,.16),transparent 20%),
    linear-gradient(135deg,#312e81,#4338ca 50%,#2563eb);
}
.member-hero .hero-badge{background:rgba(255,255,255,.15)}
@media(max-width:1100px){
  .section-grid{grid-template-columns:1fr}
  .topbar-search{display:none}
}
@media(max-width:760px){
  .form-grid,.profile-grid,.profile-details,.kpi-strip{grid-template-columns:1fr}
  .profile-grid{display:block}
  .profile-card{margin-bottom:16px}
}
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

ICONS={
    "dashboard":"<svg class='icon' viewBox='0 0 24 24'><rect x='3' y='3' width='7' height='7' rx='2'/><rect x='14' y='3' width='7' height='7' rx='2'/><rect x='3' y='14' width='7' height='7' rx='2'/><rect x='14' y='14' width='7' height='7' rx='2'/></svg>",
    "book":"<svg class='icon' viewBox='0 0 24 24'><path d='M4 19.5A2.5 2.5 0 0 1 6.5 17H20'/><path d='M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'/></svg>",
    "tag":"<svg class='icon' viewBox='0 0 24 24'><path d='M20 12l-8 8-9-9V4h7z'/><circle cx='7.5' cy='8.5' r='1.5'/></svg>",
    "users":"<svg class='icon' viewBox='0 0 24 24'><path d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'/><circle cx='9' cy='7' r='4'/><path d='M22 21v-2a4 4 0 0 0-3-3.87'/><path d='M16 3.13a4 4 0 0 1 0 7.75'/></svg>",
    "swap":"<svg class='icon' viewBox='0 0 24 24'><path d='M7 7h11l-3-3'/><path d='M17 17H6l3 3'/></svg>",
    "plus":"<svg class='icon' viewBox='0 0 24 24'><circle cx='12' cy='12' r='9'/><path d='M12 8v8M8 12h8'/></svg>",
    "alert":"<svg class='icon' viewBox='0 0 24 24'><path d='M10.3 3.7 2.5 17.2A2 2 0 0 0 4.2 20h15.6a2 2 0 0 0 1.7-2.8L13.7 3.7a2 2 0 0 0-3.4 0z'/><path d='M12 9v4M12 17h.01'/></svg>",
    "profile":"<svg class='icon' viewBox='0 0 24 24'><circle cx='12' cy='8' r='4'/><path d='M4 21a8 8 0 0 1 16 0'/></svg>",
    "settings":"<svg class='icon' viewBox='0 0 24 24'><circle cx='12' cy='12' r='3'/><path d='M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9A1.7 1.7 0 0 0 21 10h.2v4H21a1.7 1.7 0 0 0-1.6 1z'/></svg>",
    "logout":"<svg class='icon' viewBox='0 0 24 24'><path d='M10 17l5-5-5-5'/><path d='M15 12H3'/><path d='M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4'/></svg>",
    "search":"<svg class='icon' viewBox='0 0 24 24'><circle cx='11' cy='11' r='7'/><path d='m20 20-3.5-3.5'/></svg>",
    "clock":"<svg class='icon' viewBox='0 0 24 24'><circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/></svg>"
}

def icon(name):
    return ICONS.get(name,"")

def nav(user):
    if not user:
        return ""
    links=[("dashboard","Dashboard","/dashboard"),("book","Books","/books")]
    if user["role"]=="Member":
        links += [("profile","My Profile","/my/profile"),("clock","My Loans","/my/loans")]
    if user["role"] in ("Admin","Librarian"):
        links += [("tag","Categories","/categories"),("users","Members","/members"),("swap","Loans","/loans"),("plus","Borrow","/borrow"),("alert","Overdue","/overdue")]
    if user["role"]=="Admin":
        links += [("settings","Users","/users")]
    links += [("logout","Logout","/logout")]
    out=[]
    for icon_name,label,url in links:
        cls="logout" if url=="/logout" else ""
        out.append(f'<a class="{cls}" href="{url}"><span class="nav-icon">{icon(icon_name)}</span><span class="nav-text">{esc(label)}</span></a>')
    return "".join(out)

def page(title,body,user=None):
    if not user:
        return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{esc(title)} — {APP_TITLE}</title><style>{CSS}</style></head><body>{body}</body></html>"
    who=f'{esc(user["username"])} · {esc(user["role"])}'
    return f"""<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{esc(title)} — {APP_TITLE}</title>
<style>{CSS}</style>
</head>
<body>
<div class='app-shell'>
  <aside class='sidebar'>
    <div class='brand'>
      <div class='brand-mark'>{icon("book")}</div>
      <div>
        <div class='brand-title'>Library LMS</div>
        <div class='brand-sub'>MANAGEMENT SYSTEM</div>
      </div>
    </div>
    <div class='user-card'>
      <div class='user-name'>{esc(user["username"])}</div>
      <div class='user-role'>{esc(user["role"])}</div>
    </div>
    <nav class='side-nav'>{nav(user)}</nav>
    <div class='sidebar-foot'>Academic Project · 2026<br>Library Management System</div>
  </aside>
  <section class='workspace'>
    <header class='topbar'>
      <div class='topbar-left'>
        <div class='topbar-title'><h1>{esc(title)}</h1><small>Library Management Workspace</small></div>
      </div>
      <form class='topbar-search' method='get' action='/books'>
        {icon("search")}
        <input name='q' placeholder='Search books, authors, categories'>
        <button>Search</button>
      </form>
      <div class='topbar-meta'>Signed in as <b>{who}</b></div>
    </header>
    <main>{body}</main>
    <div class='footer'>Library Management System · Academic Reference Build</div>
  </section>
</div>
</body>
</html>"""

def login_view(error=""):
    err=f"<div class='alert'><span class='error'>{esc(error)}</span></div>" if error else ""
    return f"""<div class='login-wrap'>
  <section class='login-visual'>
    <div class='login-logo'>{icon("book")}</div>
    <div class='hero-badge'>Academic Library Platform</div>
    <h1>Library Management<br>System</h1>
    <p>Manage books, members, circulation, availability, and overdue loans through one modern workspace built for a public library.</p>
    <div class='feature-list'>
      <div class='feature-item'>✓ Secure role-based access</div>
      <div class='feature-item'>✓ Smart book search</div>
      <div class='feature-item'>✓ Borrowing & returns</div>
      <div class='feature-item'>✓ Member self-service</div>
    </div>
  </section>
  <section class='login-panel'>
    <div class='login-card'>
      <div class='eyebrow'>Library LMS · 2026</div>
      <h2>Welcome back</h2>
      <p class='intro'>Sign in with your library account to continue.</p>
      {err}
      <form method='post' action='/login'>
        <label>Username</label>
        <input name='username' autocomplete='username' placeholder='Enter your username' required>
        <label>Password</label>
        <input type='password' name='password' autocomplete='current-password' placeholder='Enter your password' required>
        <button>Sign in securely →</button>
      </form>
      <div class='demo-accounts'>
        <div class='demo-account'><b>Administrator</b><code>admin · Admin@12345</code></div>
        <div class='demo-account'><b>Librarian</b><code>librarian · Lib@12345</code></div>
        <div class='demo-account'><b>Member</b><code>member · Member@12345</code></div>
      </div>
    </div>
  </section>
</div>"""

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
            return self.send_html(page("Login",login_view()))
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
            if u["role"]=="Member":
                m=self.db.member_for_user(u["id"])
                rows=self.db.loans(m["id"] if m else -1)
                open_loans=[r for r in rows if r["return_date"] is None]
                overdue_loans=[r for r in open_loans if r["overdue"]]
                member_name=m["full_name"] if m else u["username"]
                status=m["status"] if m else "Not linked"
                body=f"""
<div class='hero member-hero'>
  <div class='hero-badge'>Member portal</div>
  <h2>Hello, {esc(member_name)}</h2>
  <p>Search the library collection and keep track of your current and previous loans.</p>
</div>
<div class='stats-grid'>
  <div class='stat-card'><div><div class='metric'>{len(rows)}</div><div class='metric-label'>Total loans</div></div><div class='stat-icon'>{icon("book")}</div></div>
  <div class='stat-card success'><div><div class='metric'>{len(open_loans)}</div><div class='metric-label'>Current loans</div></div><div class='stat-icon'>{icon("clock")}</div></div>
  <div class='stat-card danger'><div><div class='metric'>{len(overdue_loans)}</div><div class='metric-label'>Overdue</div></div><div class='stat-icon'>{icon("alert")}</div></div>
  <div class='stat-card cyan'><div><div class='metric'>{esc(status)}</div><div class='metric-label'>Membership status</div></div><div class='stat-icon'>{icon("profile")}</div></div>
</div>
<div class='section-grid'>
  <div class='card'>
    <div class='card-head'><div><h3 style='margin-bottom:5px'>My current loans</h3><div class='small'>Books currently checked out to your account</div></div><a class='btn secondary' href='/my/loans'>View all</a></div>
    <div class='activity-list'>
      {("".join(f"<div class='activity-item'><div class='activity-dot'>{icon('book')}</div><div><div class='activity-title'>{esc(r['book'])}</div><div class='activity-sub'>Due {esc(r['due_date'])}</div></div><span class='soft-chip'>{'Overdue' if r['overdue'] else 'Open'}</span></div>" for r in open_loans[:5]) if open_loans else "<div class='empty'>You do not have any current loans.</div>")}
    </div>
  </div>
  <div class='card insight-card'>
    <h3>Member shortcuts</h3>
    <p>Everything you need for your personal library activity.</p>
    <div class='quick-actions'>
      <a class='btn' href='/books'>{icon("search")} Search books</a>
      <a class='btn secondary' href='/my/profile'>{icon("profile")} My profile</a>
      <a class='btn secondary' href='/my/loans'>{icon("clock")} My loans</a>
    </div>
  </div>
</div>"""
            else:
                c=self.db.counts()
                recent=self.db.loans()[:5]
                role_text="Full administration and library oversight" if u["role"]=="Admin" else "Daily circulation and collection operations"
                body=f"""
<div class='hero'>
  <div class='hero-badge'>● System operational</div>
  <h2>Good to see you, {esc(u["username"])}</h2>
  <p>{role_text}. Monitor the most important library activity from one professional dashboard.</p>
</div>
<div class='stats-grid'>
  <div class='stat-card'><div><div class='metric'>{c['books']}</div><div class='metric-label'>Books</div></div><div class='stat-icon'>{icon("book")}</div></div>
  <div class='stat-card cyan'><div><div class='metric'>{c['members']}</div><div class='metric-label'>Members</div></div><div class='stat-icon'>{icon("users")}</div></div>
  <div class='stat-card success'><div><div class='metric'>{c['open']}</div><div class='metric-label'>Open loans</div></div><div class='stat-icon'>{icon("swap")}</div></div>
  <div class='stat-card danger'><div><div class='metric'>{c['overdue']}</div><div class='metric-label'>Overdue loans</div></div><div class='stat-icon'>{icon("alert")}</div></div>
</div>
<div class='section-grid'>
  <div class='card'>
    <div class='card-head'>
      <div><h3 style='margin-bottom:5px'>Recent circulation</h3><div class='small'>Latest borrowing activity in the library</div></div>
      <a class='btn secondary' href='/loans'>View loans</a>
    </div>
    <div class='activity-list'>
      {("".join(f"<div class='activity-item'><div class='activity-dot'>{icon('swap')}</div><div><div class='activity-title'>{esc(r['book'])}</div><div class='activity-sub'>{esc(r['member'])} · Due {esc(r['due_date'])}</div></div><span class='soft-chip'>{'Returned' if r['return_date'] else ('Overdue' if r['overdue'] else 'Open')}</span></div>" for r in recent) if recent else "<div class='empty'>No circulation activity yet.</div>")}
    </div>
  </div>
  <div class='card insight-card'>
    <h3>Quick operations</h3>
    <p>Start the most common library tasks without leaving the dashboard.</p>
    <div class='quick-actions'>
      <a class='btn' href='/borrow'>{icon("plus")} Borrow book</a>
      <a class='btn secondary' href='/books'>{icon("book")} Books</a>
      <a class='btn secondary' href='/members'>{icon("users")} Members</a>
      <a class='btn secondary' href='/overdue'>{icon("alert")} Overdue</a>
    </div>
    <div style='margin-top:18px'>
      <div class='insight-mini'><span>Collection status</span><strong>{c['books']} titles</strong></div>
      <div class='insight-mini'><span>Active circulation</span><strong>{c['open']} open</strong></div>
      <div class='insight-mini'><span>Needs attention</span><strong>{c['overdue']} overdue</strong></div>
    </div>
  </div>
</div>"""
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
            initials=((m['full_name'] if m else u['username'])[:1] or "M").upper()
            body=f"""<div class='page-head'><div><h2>My Profile</h2><p>Your personal library membership information</p></div></div>
<div class='profile-grid'>
  <div class='profile-card'>
    <div class='avatar'>{esc(initials)}</div>
    <div class='profile-name'>{esc(m['full_name'] if m else u['username'])}</div>
    <div class='profile-role'>Library Member</div>
  </div>
  <div class='card'>
    <div class='card-head'><div><h3 style='margin-bottom:5px'>Membership details</h3><div class='small'>Read-only account information</div></div><span class='badge ok'>{esc(m['status'] if m else '')}</span></div>
    <div class='profile-details'>
      <div class='detail-box'><div class='detail-label'>Full name</div><div class='detail-value'>{esc(m['full_name'] if m else '')}</div></div>
      <div class='detail-box'><div class='detail-label'>Phone</div><div class='detail-value'>{esc(m['phone'] if m else '')}</div></div>
      <div class='detail-box'><div class='detail-label'>Registration date</div><div class='detail-value'>{esc(m['registration_date'] if m else '')}</div></div>
      <div class='detail-box'><div class='detail-label'>Status</div><div class='detail-value'>{esc(m['status'] if m else '')}</div></div>
    </div>
  </div>
</div>"""
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
                    return self.send_html(page("Login",login_view(err)),401)
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
