import React, {useEffect, useState} from 'react';
import { Home, FlaskConical, Package, ShoppingCart, FileText, Users, Truck, Download, BarChart3, Settings, Monitor, Bell, Search, Bot, ClipboardList, Factory } from 'lucide-react';
import { createRoot } from 'react-dom/client';
import './style.css';

const menu = [
  ['Dashboard', Home], ['Gereed product', FlaskConical], ['Tanken', Factory], ['Recepturen', ClipboardList], ['Verpakkingen', Package], ['Orders', ShoppingCart], ['Pakbonnen', FileText], ['Facturen', FileText], ['Klanten', Users], ['Leveranciers', Truck], ['Inkoop', Download], ['Rapportages', BarChart3], ['Instellingen', Settings]
];

function StatusBadge({children}) {
  const cls = children === 'Bijna op' ? 'danger' : children === 'Bestellen' ? 'warning' : children === 'Ruim voldoende' ? 'strong' : 'ok';
  return <span className={`badge ${cls}`}>{children}</span>
}

function ProductIcon({type}){
  return <div className={`productIcon ${type || 'blue'}`}></div>
}

function TankRow({tank}){
  const pct = Math.round((tank.liters / tank.capacity) * 100);
  return <div className="tankRow">
    <div className="tankIcon"><div className="tankFill" style={{height: `${pct}%`}} /></div>
    <div className="tankBody">
      <div className="rowTitle"><b>{tank.name}</b><b>{tank.liters.toLocaleString('nl-NL')} L</b></div>
      <div className="bar"><div style={{width: `${pct}%`}} /></div>
      <div className="muted">Capaciteit: {tank.capacity.toLocaleString('nl-NL')} L <span>{pct}%</span></div>
    </div>
  </div>
}

function App(){
  const [data, setData] = useState(null);
  useEffect(()=>{fetch('/api/dashboard').then(r=>r.json()).then(setData).catch(()=>setData(null))},[]);
  if(!data) return <div className="loading">GROBÉ OS laden...</div>;
  return <div className="app">
    <aside className="sidebar">
      <div className="brand"><div>GROBÉ OS</div><small>OPERATING SYSTEM</small></div>
      <nav>{menu.map(([label, Icon], i)=><button key={label} className={i===0?'active':''}><Icon size={22}/><span>{label}</span></button>)}</nav>
      <div className="system"><Monitor size={22}/> <span>Systeemstatus</span></div>
      <div className="version">v0.1 React</div>
    </aside>
    <main>
      <header className="topbar">
        <div className="hamb">☰</div>
        <div className="hello"><b>Goedemorgen Ron</b><span>Dinsdag 8 juli 2026</span></div>
        <div className="search"><span>Zoek product, klant, leverancier, pakbon, factuur...</span><Search size={24}/></div>
        <button className="ai"><Bot size={18}/> AI Assist</button>
        <div className="bell"><Bell/><em>3</em></div>
        <div className="user">RM</div><div className="username">Ron⌄</div>
      </header>
      <section className="content">
        <div className="kpis">{data.kpis.map(k=><div className="kpi" key={k.label}><div className="circle">{k.icon}</div><div><small>{k.label}</small><h2>{k.value}</h2><p className={k.trend}>{k.sub}</p><div className="spark"></div></div></div>)}</div>
        <div className="grid3">
          <Card title="Gereed product voorraad" link="Alle producten bekijken">
            {data.finishedProducts.map(p=><div className="listRow" key={p.name}><ProductIcon type={p.type}/><div><b>{p.name}</b><span>{p.qty}</span></div><StatusBadge>{p.status}</StatusBadge></div>)}
          </Card>
          <Card title="Tanken" link="Alle tanks bekijken">
            {data.tanks.map(t=><TankRow tank={t} key={t.name}/>) }
          </Card>
          <Card title="Verpakkingsvoorraad" link="Alle verpakkingen bekijken">
            {data.packaging.map(p=><div className="listRow" key={p.name}><div className="emoji">{p.icon}</div><div><b>{p.name}</b><span>{p.qty}</span></div><StatusBadge>{p.status}</StatusBadge></div>)}
          </Card>
        </div>
        <div className="bottomGrid">
          <Card title="Meldingen" smallLink="Bekijk alles">
            {data.alerts.map(a=><div className="alert" key={a.text}><span className={a.level}>{a.level==='danger'?'!':a.level==='warning'?'!':'i'}</span>{a.text}</div>)}
          </Card>
          <Card title="Recente activiteit" smallLink="Bekijk alles">
            {data.activity.map(a=><div className="activity" key={a.time}><b>{a.time}</b><span>{a.text}</span></div>)}
          </Card>
          <Card title="Snel acties">
            <div className="actions"><button>Nieuwe pakbon</button><button>Nieuwe order</button><button>Afvulling registreren</button><button>Inkoopfactuur importeren</button><button>Excel importeren</button><button>Nieuwe klant</button></div>
          </Card>
        </div>
      </section>
    </main>
  </div>
}

function Card({title, children, link, smallLink}){return <section className="card"><div className="cardHead"><h3>{title}</h3>{smallLink&&<a>{smallLink} →</a>}</div>{children}{link&&<a className="more">{link} →</a>}</section>}

createRoot(document.getElementById('root')).render(<App/>);
