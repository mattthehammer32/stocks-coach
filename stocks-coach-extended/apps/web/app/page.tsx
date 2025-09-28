
import CoachChart from "../components/CoachChart";
import NewsPanel from "../components/NewsPanel";


async function getNews(symbol: string = "AAPL") {
  const url = `${process.env.NEXT_PUBLIC_API_URL}/news/${symbol}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`News API error ${res.status}`);
  return res.json();
}

async function getHistory(symbol: string = "AAPL") {
  const url = `${process.env.NEXT_PUBLIC_API_URL}/history/${symbol}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export default async function Page() {
  const [data, news] = await Promise.all([getHistory("AAPL"), getNews("AAPL")]);
  return (
    <main style={{ padding: 16 }}>
      <h1>Stocks Coach</h1>
      <p style={{opacity:.8, marginBottom:12}}>Clean real-time chart with highs/lows and entry/exit markers.</p>
      <CoachChart data={data} />
      <section style={{marginTop:16}}>
        <h2>News & AI Take</h2>
        <NewsPanel items={news} />
      </section>
    </main>
  );
}
