
'use client';
import { useEffect, useMemo, useRef, useState } from 'react';
import { createChart, ColorType, UTCTimestamp } from 'lightweight-charts';

type Bar = { time: UTCTimestamp, open:number, high:number, low:number, close:number };
type LinePt = { time: UTCTimestamp, value:number };

export default function CoachChart({ data }: { data: any }) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ReturnType<typeof createChart>>();
  const candleRef = useRef<any>(); const smaRef = useRef<any>(); const h52Ref = useRef<any>(); const l52Ref = useRef<any>();
  const [why, setWhy] = useState<string[] | null>(null);

  const colors = useMemo(() => ({
    grid:'#2b2f36', text:'#c7cdd6', up:'#26a69a', down:'#ef5350', sma:'#8ab4f8', band:'#7e8794'
  }), []);

  useEffect(() => {
    if (!ref.current) return;
    const chart = createChart(ref.current, {
      width: ref.current.clientWidth, height: 480,
      layout: { background: { type: ColorType.Solid, color: 'transparent' }, textColor: colors.text },
      grid: { vertLines: { color: colors.grid }, horzLines: { color: colors.grid } },
      rightPriceScale: { borderColor: colors.grid }, timeScale: { borderColor: colors.grid, rightOffset: 8, barSpacing: 6 }
    });
    chartRef.current = chart;

    const candles = chart.addCandlestickSeries({ upColor: colors.up, downColor: colors.down, borderVisible:false, wickUpColor:colors.up, wickDownColor:colors.down });
    const sma = chart.addLineSeries({ color: colors.sma, lineWidth: 2 });
    const h52 = chart.addLineSeries({ color: colors.band, lineWidth: 1, lineStyle: 1 });
    const l52 = chart.addLineSeries({ color: colors.band, lineWidth: 1, lineStyle: 1 });
    candleRef.current = candles; smaRef.current = sma; h52Ref.current = h52; l52Ref.current = l52;

    const toTs = (ms:number)=> Math.floor(ms/1000) as UTCTimestamp;
    const bars: Bar[] = data.timestamps.map((t:number, i:number) => ({
      time: toTs(t), open:data.open[i], high:data.high[i], low:data.low[i], close:data.close[i]
    }));
    const sma52: LinePt[] = data.timestamps.map((t:number, i:number)=>({ time: toTs(t), value: data.sma52[i]})).filter((p:any)=>Number.isFinite(p.value));
    const h52d: LinePt[]  = data.timestamps.map((t:number, i:number)=>({ time: toTs(t), value: data.h52[i]})).filter((p:any)=>Number.isFinite(p.value));
    const l52d: LinePt[]  = data.timestamps.map((t:number, i:number)=>({ time: toTs(t), value: data.l52[i]})).filter((p:any)=>Number.isFinite(p.value));

    candles.setData(bars); sma.setData(sma52); h52Ref.current.setData(h52d); l52Ref.current.setData(l52d);

    // Swing high/low pins
    const markers: any[] = [];
    for (const i of data.swing_high_idx) markers.push({ time: bars[i].time, position:'aboveBar', color:'#9aa0a6', shape:'circle', text:'SH' });
    for (const i of data.swing_low_idx)  markers.push({ time: bars[i].time, position:'belowBar', color:'#9aa0a6', shape:'circle', text:'SL' });

    // Entry/Exit markers + Coach text
    if (data.signals?.length) {
      for (const s of data.signals) {
        markers.push({
          time: s.time as UTCTimestamp,
          position: s.kind === 'ENTRY' ? 'belowBar' : 'aboveBar',
          color: s.kind === 'ENTRY' ? '#26a69a' : '#ef5350',
          shape: s.kind === 'ENTRY' ? 'arrowUp' : 'arrowDown',
          text: s.kind
        });
      }
      const last = data.signals[data.signals.length - 1];
      setWhy(last.why ?? null);
    }
    candles.setMarkers(markers);
    chart.timeScale().fitContent();

    // Resize
    const ro = new ResizeObserver((e)=> chart.applyOptions({ width: e[0].contentRect.width }));
    ro.observe(ref.current);

    // Optional demo websocket (replace host if not same origin)
    let wsUrl = '';
    try {
      const loc = window.location;
      wsUrl = `${loc.protocol === 'https:' ? 'wss' : 'ws'}://${loc.host}/stream/AAPL`;
    } catch { /* ignore */ }
    const ws = wsUrl ? new WebSocket(wsUrl) : null;
    ws && (ws.onmessage = (msg) => {
      const payload = JSON.parse(msg.data);
      if (payload.bar) candleRef.current.update({
        time: payload.bar.t as UTCTimestamp, open: payload.bar.o, high: payload.bar.h, low: payload.bar.l, close: payload.bar.c
      });
    });

    return () => { ws?.close(); ro.disconnect(); chart.remove(); };
  }, [data, colors]);

  return (
    <div style={{display:'grid', gap:12}}>
      <div ref={ref} style={{ width:'100%', height:480 }} />
      <div style={{background:'#111418', padding:12, borderRadius:8, border:'1px solid #2b2f36'}}>
        <b>Coach</b>
        <div style={{marginTop:8, color:'#c7cdd6'}}>
          {why ? (<ul>{why.map((w:string,i:number)=><li key={i}>{w}</li>)}</ul>) : 'No active signal.'}
        </div>
      </div>
    </div>
  );
}
