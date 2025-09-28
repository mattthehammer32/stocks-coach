'use client';
export default function NewsPanel({ items }: { items: any[] }) {
  if (!items?.length) return <p style={{opacity:.7}}>No news yet.</p>;
  const top = items[0];
  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#111418', padding:12, border:'1px solid #2b2f36', borderRadius:8}}>
        <b>AI Take</b>
        <div style={{opacity:.85, marginTop:8}}>
          <span style={{padding:'2px 8px', border:'1px solid #2b2f36', borderRadius:999, textTransform:'uppercase'}}>
            {top.impact} • {Math.round((top.confidence||0)*100)}%
          </span>
          <p style={{marginTop:8}}>{top.summary}</p>
        </div>
      </div>
      {items.map((n:any, i:number) => (
        <article key={i} style={{border:'1px solid #2b2f36', borderRadius:8, padding:12}}>
          <div style={{display:'flex', gap:8, alignItems:'center'}}>
            <span style={{padding:'2px 8px', border:'1px solid #2b2f36', borderRadius:999}}>{n.impact}</span>
            <small style={{opacity:.7}}>{n.source} • {new Date(n.published_at).toLocaleString()}</small>
          </div>
          <h4 style={{margin:'8px 0'}}>{n.title}</h4>
          <p style={{opacity:.9}}>{n.summary}</p>
          <a href={n.url} target="_blank" rel="noreferrer">View source</a>
        </article>
      ))}
    </div>
  );
}
