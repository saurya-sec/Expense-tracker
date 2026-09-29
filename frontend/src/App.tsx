import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, Navigate, NavLink, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowDownLeft, ArrowUpRight, BarChart3, Bot, CheckCircle2, ChevronRight,
  CircleDollarSign, Database, FileSpreadsheet, FileText, LayoutDashboard,
  LogIn, LogOut, Menu, Plus, RefreshCw, Settings, ShieldCheck, Trash2,
  Upload, Wallet, X
} from "lucide-react";
import { api, ApiRequestError } from "./api";
import { useAuth } from "./auth";
import type { Expense, ExpenseInput, ImportResponse, Income, IncomeInput } from "./types";

const money = (v: string | number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(v || 0));

const dateFmt = (v: string) =>
  new Intl.DateTimeFormat("en-US", { dateStyle: "medium" }).format(new Date(v));

function ErrorBanner({ error, onClose }: { error: string; onClose?: () => void }) {
  return <div className="alert error"><span>{error}</span>{onClose && <button className="icon-btn" onClick={onClose}><X size={16}/></button>}</div>;
}

function SuccessBanner({ children }: { children: React.ReactNode }) {
  return <div className="alert success"><CheckCircle2 size={17}/><span>{children}</span></div>;
}

function Shell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const [mobile, setMobile] = useState(false);
  const nav = [
    ["/", "Overview", LayoutDashboard],
    ["/transactions", "Transactions", BarChart3],
    ["/import", "Import", Upload],
    ["/assistant", "Assistant", Bot],
    ["/settings", "System", Settings]
  ] as const;
  return <div className="app-shell">
    <aside className={mobile ? "sidebar open" : "sidebar"}>
      <div className="brand"><div className="brand-mark"><Wallet size={20}/></div><span>Ledger</span></div>
      <nav>{nav.map(([to, label, Icon]) => <NavLink key={to} to={to} end={to === "/"} onClick={() => setMobile(false)}><Icon size={18}/><span>{label}</span></NavLink>)}</nav>
      <div className="sidebar-bottom">
        <div className="user-card"><div className="avatar">{(user?.email?.[0] || "U").toUpperCase()}</div><div><strong>{user?.email || "Local session"}</strong><small>Authenticated</small></div></div>
        <button className="logout" onClick={logout}><LogOut size={17}/> Sign out</button>
      </div>
    </aside>
    {mobile && <div className="backdrop" onClick={() => setMobile(false)}/>}
    <main className="main">
      <header className="topbar"><button className="mobile-menu icon-btn" onClick={() => setMobile(true)}><Menu/></button><div className="topbar-title">{document.title.split(" — ")[0]}</div><div className="topbar-right"><span className="status-dot"/> API connected on demand</div></header>
      <div className="content">{children}</div>
    </main>
  </div>;
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { authenticated } = useAuth();
  return authenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: React.ReactNode }) {
  return <div className="page-header"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{description && <p>{description}</p>}</div>{action}</div>;
}

function Overview() {
  const [income, setIncome] = useState<Income[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try { const [i, e] = await Promise.all([api.listIncome(), api.listExpenses()]); setIncome(i); setExpenses(e); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed to load dashboard."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { load(); }, [load]);
  const totalIncome = income.reduce((s, x) => s + Number(x.amount), 0);
  const totalExpense = expenses.reduce((s, x) => s + Number(x.amount), 0);
  const balance = totalIncome - totalExpense;
  const recent = [...income.map(x => ({...x, type:"income" as const, date:x.income_date})), ...expenses.map(x => ({...x, type:"expense" as const, date:x.expense_date}))].sort((a,b)=>+new Date(b.date)-+new Date(a.date)).slice(0,7);
  return <><PageHeader eyebrow="Financial overview" title="Good morning." description="Your income, expenses, and recent activity at a glance." action={<button className="secondary" onClick={load}><RefreshCw size={16}/> Refresh</button>}/>
    {error && <ErrorBanner error={error}/>}
    <div className="stat-grid">
      <StatCard label="Available balance" value={money(balance)} icon={<CircleDollarSign/>} tone="blue"/>
      <StatCard label="Total income" value={money(totalIncome)} icon={<ArrowDownLeft/>} tone="green"/>
      <StatCard label="Total expenses" value={money(totalExpense)} icon={<ArrowUpRight/>} tone="red"/>
      <StatCard label="Transactions" value={String(income.length + expenses.length)} icon={<BarChart3/>} tone="purple"/>
    </div>
    <div className="dashboard-grid">
      <section className="panel"><div className="panel-head"><div><h2>Recent activity</h2><p>Latest records returned by the API.</p></div><Link to="/transactions" className="text-link">View all <ChevronRight size={15}/></Link></div>
        {loading ? <LoadingRows/> : recent.length === 0 ? <Empty text="No transactions yet."/> : <div className="activity-list">{recent.map(x => <div className="activity" key={`${x.type}-${x.id}`}><div className={`activity-icon ${x.type}`} >{x.type === "income" ? <ArrowDownLeft size={17}/> : <ArrowUpRight size={17}/>}</div><div className="activity-main"><strong>{x.title || "Untitled"}</strong><span>{x.category} · {dateFmt(x.date)}</span></div><strong className={x.type === "income" ? "amount positive" : "amount negative"}>{x.type === "income" ? "+" : "-"}{money(x.amount)}</strong></div>)}</div>}
      </section>
      <section className="panel"><div className="panel-head"><div><h2>Quick actions</h2><p>Manage your ledger.</p></div></div><div className="quick-actions">
        <Link to="/transactions?new=income" className="quick"><div className="quick-icon green"><Plus/></div><div><strong>Add income</strong><span>Record money received</span></div><ChevronRight/></Link>
        <Link to="/transactions?new=expense" className="quick"><div className="quick-icon red"><Plus/></div><div><strong>Add expense</strong><span>Record money spent</span></div><ChevronRight/></Link>
        <Link to="/import" className="quick"><div className="quick-icon blue"><Upload/></div><div><strong>Import statement</strong><span>Upload eSewa or statement data</span></div><ChevronRight/></Link>
      </div></section>
    </div>
  </>;
}

function StatCard({label,value,icon,tone}:{label:string;value:string;icon:React.ReactNode;tone:string}) {
  return <div className="stat-card"><div className={`stat-icon ${tone}`}>{icon}</div><div><span>{label}</span><strong>{value}</strong></div></div>;
}

function LoadingRows(){ return <div className="skeleton-list">{[1,2,3,4].map(i=><div className="skeleton" key={i}/>)}</div>; }
function Empty({text}:{text:string}){ return <div className="empty"><FileText size={28}/><span>{text}</span></div>; }

function Transactions() {
  const params = new URLSearchParams(useLocation().search);
  const [tab, setTab] = useState<"all"|"income"|"expense">("all");
  const [income,setIncome]=useState<Income[]>([]); const [expenses,setExpenses]=useState<Expense[]>([]);
  const [loading,setLoading]=useState(true); const [error,setError]=useState("");
  const [modal,setModal]=useState<"income"|"expense"|null>(params.get("new") as any || null);
  const [editing,setEditing]=useState<Income|Expense|null>(null);
  const load=useCallback(async()=>{setLoading(true);setError("");try{const [i,e]=await Promise.all([api.listIncome(),api.listExpenses()]);setIncome(i);setExpenses(e)}catch(e){setError(e instanceof Error?e.message:"Failed to load transactions.")}finally{setLoading(false)}},[]);
  useEffect(()=>{load()},[load]);
  async function remove(type:"income"|"expense",id:number){if(!confirm("Delete this transaction?"))return;try{if(type==="income")await api.deleteIncome(id);else await api.deleteExpense(id);await load()}catch(e){setError(e instanceof Error?e.message:"Delete failed.")}}
  const rows=[...income.map(x=>({type:"income" as const,data:x,date:x.income_date})),...expenses.map(x=>({type:"expense" as const,data:x,date:x.expense_date}))].sort((a,b)=>+new Date(b.date)-+new Date(a.date)).filter(x=>tab==="all"||x.type===tab);
  return <><PageHeader eyebrow="Ledger" title="Transactions" description="Create, update, inspect, and delete records through the FastAPI CRUD endpoints." action={<div className="actions"><button className="secondary" onClick={load}><RefreshCw size={16}/> Refresh</button><button className="primary" onClick={()=>setModal("income")}><Plus size={16}/> Add transaction</button></div>}/>
  {error&&<ErrorBanner error={error}/>}<div className="panel table-panel"><div className="tabs"><button className={tab==="all"?"active":""} onClick={()=>setTab("all")}>All <b>{income.length+expenses.length}</b></button><button className={tab==="income"?"active":""} onClick={()=>setTab("income")}>Income <b>{income.length}</b></button><button className={tab==="expense"?"active":""} onClick={()=>setTab("expense")}>Expenses <b>{expenses.length}</b></button></div>
  {loading?<LoadingRows/>:rows.length===0?<Empty text="No matching transactions."/>:<div className="table-wrap"><table><thead><tr><th>Transaction</th><th>Category</th><th>Date</th><th>Amount</th><th></th></tr></thead><tbody>{rows.map(r=><tr key={`${r.type}-${r.data.id}`}><td><div className="table-title"><span className={`mini-icon ${r.type}`}>{r.type==="income"?<ArrowDownLeft size={14}/>:<ArrowUpRight size={14}/>}</span><div><strong>{r.data.title||"Untitled"}</strong><small>{r.data.description||"No description"}</small></div></div></td><td><span className="pill">{r.data.category}</span></td><td>{dateFmt(r.date)}</td><td className={r.type==="income"?"amount positive":"amount negative"}>{r.type==="income"?"+":"-"}{money(r.data.amount)}</td><td><div className="row-actions"><button className="icon-btn" title="Edit" onClick={()=>{setEditing(r.data);setModal(r.type)}}><Settings size={16}/></button><button className="icon-btn danger-icon" title="Delete" onClick={()=>remove(r.type,r.data.id)}><Trash2 size={16}/></button></div></td></tr>)}</tbody></table></div>}</div>
  {modal&&<TransactionModal type={modal} initial={editing} onClose={()=>{setModal(null);setEditing(null)}} onSaved={async()=>{setModal(null);setEditing(null);await load()}}/>}</>;
}

function TransactionModal({type,initial,onClose,onSaved}:{type:"income"|"expense";initial:Income|Expense|null;onClose:()=>void;onSaved:()=>Promise<void>}) {
  const editing=Boolean(initial);
  const [form,setForm]=useState<any>(()=>type==="income"?{title:initial?.title||"",amount:initial?.amount||"",category:initial?.category||"",description:initial?.description||"",income_date:(initial as Income)?.income_date||new Date().toISOString().slice(0,10)}:{title:initial?.title||"",amount:initial?.amount||"",category:initial?.category||"",description:initial?.description||"",expense_date:(initial as Expense)?.expense_date||new Date().toISOString().slice(0,10)});
  const [error,setError]=useState(""); const [saving,setSaving]=useState(false);
  async function submit(e:React.FormEvent){e.preventDefault();setSaving(true);setError("");try{const data={...form,amount:Number(form.amount)};if(type==="income") editing?await api.updateIncome(initial!.id,data as IncomeInput):await api.createIncome(data as IncomeInput);else editing?await api.updateExpense(initial!.id,data as ExpenseInput):await api.createExpense(data as ExpenseInput);await onSaved()}catch(e){setError(e instanceof Error?e.message:"Save failed.")}finally{setSaving(false)}}
  return <div className="modal-backdrop"><div className="modal"><div className="modal-head"><div><div className="eyebrow">{editing?"Edit":"New"} {type}</div><h2>{editing?"Update":"Record"} {type}</h2></div><button className="icon-btn" onClick={onClose}><X/></button></div>{error&&<ErrorBanner error={error}/>}<form onSubmit={submit}><div className="form-grid"><Field label="Title"><input required value={form.title} onChange={e=>setForm({...form,title:e.target.value})}/></Field><Field label="Amount"><input required min="0" step="0.01" type="number" value={form.amount} onChange={e=>setForm({...form,amount:e.target.value})}/></Field><Field label="Category"><input required value={form.category} placeholder="salary, food, others..." onChange={e=>setForm({...form,category:e.target.value})}/></Field><Field label="Date"><input required type="date" value={type==="income"?form.income_date:form.expense_date} onChange={e=>setForm({...form,[type==="income"?"income_date":"expense_date"]:e.target.value})}/></Field></div><Field label="Description"><textarea rows={4} value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></Field><div className="modal-actions"><button type="button" className="secondary" onClick={onClose}>Cancel</button><button className="primary" disabled={saving}>{saving?"Saving…":editing?"Update":"Create"}</button></div></form></div></div>;
}
function Field({label,children}:{label:string;children:React.ReactNode}){return <label className="field"><span>{label}</span>{children}</label>}

function ImportPage() {
  const [type,setType]=useState<"esewa"|"statement">("esewa"); const [file,setFile]=useState<File|null>(null);
  const [busy,setBusy]=useState(false); const [error,setError]=useState(""); const [result,setResult]=useState<ImportResponse|null>(null);
  async function submit(){if(!file){setError("Choose a file first.");return}setBusy(true);setError("");setResult(null);try{if(type==="esewa"){setResult(await api.uploadEsewa(file))}else{await api.uploadStatement(file);setError("Statement upload completed without a structured success payload.")}}catch(e){setError(e instanceof Error?e.message:"Upload failed.")}finally{setBusy(false)}}
  return <><PageHeader eyebrow="Data import" title="Import statements" description="Send files directly to the documented multipart/form-data endpoints."/>
  {error&&<ErrorBanner error={error}/>} {result&&<SuccessBanner>{result.message} · {result.total_transactions} transactions, {result.income_created} income, {result.expenses_created} expenses created.</SuccessBanner>}
  <div className="import-grid"><section className="panel import-card"><div className="import-icon"><FileSpreadsheet/></div><h2>eSewa statement</h2><p>Uses <code>POST /esewa/upload</code>. The backend currently returns transaction counts after import.</p><div className="segmented"><button className={type==="esewa"?"selected":""} onClick={()=>setType("esewa")}>eSewa</button><button className={type==="statement"?"selected":""} onClick={()=>setType("statement")}>Generic statement</button></div>
  <label className="dropzone"><Upload size={25}/><strong>{file?.name||"Choose a statement file"}</strong><span>Click to browse your device</span><input type="file" accept={type==="esewa"?".xls,.xlsx,.csv":".pdf"} onChange={e=>setFile(e.target.files?.[0]||null)}/></label><button className="primary full" disabled={busy||!file} onClick={submit}>{busy?"Uploading…":"Upload statement"}</button></section>
  <section className="panel import-info"><h2>Integration notes</h2><Info icon={<ShieldCheck/>} title="No mocked success" text="Every result shown here comes from the FastAPI response. HTTP errors are rendered verbatim."/><Info icon={<Database/>} title="eSewa endpoint" text="POST /esewa/upload accepts a multipart field named file."/><Info icon={<FileText/>} title="Generic statement endpoint" text="POST /statement/upload is wired, but the supplied backend run rejected the tested XLS file as a non-PDF."/><Info icon={<Bot/>} title="Authentication" text="Only the /chat endpoint is documented with a Bearer token requirement."/>
  </section></div></>;
}
function Info({icon,title,text}:{icon:React.ReactNode;title:string;text:string}){return <div className="info-row"><div>{icon}</div><span><strong>{title}</strong><small>{text}</small></span></div>}

function Assistant() {
  const [messages,setMessages]=useState<{role:"user"|"assistant";text:string}[]>([]);
  const [input,setInput]=useState(""); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
  async function send(e?:React.FormEvent){e?.preventDefault();const message=input.trim();if(!message||busy)return;setInput("");setError("");setMessages(m=>[...m,{role:"user",text:message}]);setBusy(true);try{const r=await api.chat(message);setMessages(m=>[...m,{role:"assistant",text:r.response}])}catch(e){setError(e instanceof Error?e.message:"Chat request failed.")}finally{setBusy(false)}}
  return <><PageHeader eyebrow="AI assistant" title="Ask your ledger" description="Authenticated requests are sent to POST /chat."/><div className="chat panel"><div className="chat-messages">{messages.length===0?<div className="chat-empty"><div className="bot-icon"><Bot/></div><h2>What would you like to know?</h2><p>Ask for income, expense, totals, or other analysis supported by your backend.</p><div className="suggestions">{["Give all income","Show my expenses","Summarize my transactions"].map(x=><button key={x} onClick={()=>setInput(x)}>{x}</button>)}</div></div>:messages.map((m,i)=><div className={`bubble-row ${m.role}`} key={i}><div className="bubble">{m.text}</div></div>)}{busy&&<div className="bubble-row assistant"><div className="bubble typing">Thinking…</div></div>}</div>{error&&<ErrorBanner error={error}/>}<form className="chat-input" onSubmit={send}><input value={input} onChange={e=>setInput(e.target.value)} placeholder="Ask about your finances…" disabled={busy}/><button className="primary" disabled={!input.trim()||busy}>Send</button></form></div></>;
}

function SettingsPage(){
  const {user}=useAuth(); const [apiStatus,setApiStatus]=useState<"idle"|"ok"|"error">("idle"); const [message,setMessage]=useState("");
  async function check(){setApiStatus("idle");setMessage("");try{const r=await api.root();setMessage(r.message);setApiStatus("ok")}catch(e){setMessage(e instanceof Error?e.message:"API unavailable");setApiStatus("error")}}
  return <><PageHeader eyebrow="System" title="Settings & diagnostics" description="Verify the API connection without hiding backend failures."/><div className="settings-grid"><section className="panel"><h2>Session</h2><div className="setting-line"><div><strong>Signed in as</strong><span>{user?.email||"Unknown"}</span></div><ShieldCheck className="good"/></div><div className="setting-line"><div><strong>Access token</strong><span>Stored locally for the current browser</span></div><span className="pill green-pill">Present</span></div></section><section className="panel"><h2>API diagnostics</h2><div className="setting-line"><div><strong>GET /</strong><span>FastAPI root health</span></div><button className="secondary" onClick={check}><RefreshCw size={15}/> Test</button></div>{apiStatus!=="idle"&&<div className={`diagnostic ${apiStatus}`}>{apiStatus==="ok"?<CheckCircle2/>:<X/>}<span>{message}</span></div>}</section></div></>;
}

function Login(){
  const {login,signup,authenticated}=useAuth(); const nav=useNavigate(); const [mode,setMode]=useState<"login"|"signup">("login"); const [email,setEmail]=useState("");const [password,setPassword]=useState("");const [busy,setBusy]=useState(false);const [error,setError]=useState("");const [notice,setNotice]=useState("");
  if(authenticated)return <Navigate to="/" replace/>;
  async function submit(e:React.FormEvent){e.preventDefault();setBusy(true);setError("");setNotice("");try{if(mode==="login"){await login(email,password);nav("/")}else{await signup(email,password);setNotice("Signup request succeeded. You can now sign in.");setMode("login")}}catch(e){setError(e instanceof Error?e.message:"Authentication failed.")}finally{setBusy(false)}}
  return <div className="auth-page"><div className="auth-art"><div className="brand"><div className="brand-mark"><Wallet size={20}/></div><span>Ledger</span></div><div><div className="eyebrow">Personal finance</div><h1>A clean ledger for every transaction.</h1><p>Connect your FastAPI backend and keep income, expenses, imports, and financial queries in one workspace.</p></div><div className="auth-proof"><CheckCircle2/><span>Strict API integration · no demo data</span></div></div><div className="auth-form-wrap"><div className="auth-form"><div className="mobile-brand brand"><div className="brand-mark"><Wallet size={20}/></div><span>Ledger</span></div><div className="eyebrow">{mode==="login"?"Welcome back":"Create account"}</div><h1>{mode==="login"?"Sign in":"Create your account"}</h1><p>{mode==="login"?"Use your FastAPI account to continue.":"Create an account through POST /auth/signup."}</p>{error&&<ErrorBanner error={error}/>} {notice&&<SuccessBanner>{notice}</SuccessBanner>}<form onSubmit={submit}><Field label="Email"><input required type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com"/></Field><Field label="Password"><input required minLength={6} type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="••••••••"/></Field><button className="primary full" disabled={busy}>{busy?"Please wait…":mode==="login"?"Sign in":"Create account"}</button></form><button className="switch-auth" onClick={()=>{setMode(mode==="login"?"signup":"login");setError("");setNotice("")}}>{mode==="login"?"Need an account? Sign up":"Already have an account? Sign in"}</button></div></div></div>;
}

export default function App(){
  return <Routes><Route path="/login" element={<Login/>}/><Route path="/*" element={<RequireAuth><Shell><Routes><Route index element={<Overview/>}/><Route path="transactions" element={<Transactions/>}/><Route path="import" element={<ImportPage/>}/><Route path="assistant" element={<Assistant/>}/><Route path="settings" element={<SettingsPage/>}/></Routes></Shell></RequireAuth>}/></Routes>;
}