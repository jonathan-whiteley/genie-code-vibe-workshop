// Homebase app — Guest feedback module.

const Stars = ({ n, size = 14 }) => (
  <div style={{ display:'inline-flex', gap:1 }}>
    {[1,2,3,4,5].map(i => <Icon key={i} name="star" size={size} color={i<=n?'var(--db-yellow-600)':'var(--db-gray-lines)'} stroke={0} style={{ fill: i<=n?'var(--db-yellow-600)':'var(--db-gray-lines)' }} />)}
  </div>
);
const SENT = { pos:{ fg:'var(--db-green-800)', bg:'var(--db-green-300)', label:'Positive' }, neu:{ fg:'var(--db-yellow-800)', bg:'var(--db-yellow-300)', label:'Neutral' }, neg:{ fg:'var(--db-lava-700)', bg:'var(--db-lava-300)', label:'Needs care' } };

/* ============================ Sentiment timeline (stacked area) ============================ */
const SENT_FILL = { pos:'#34B98B', neu:'#C7CDD0', neg:'#FF8A78' };
const SENT_LINE = { pos:'#1F9E73', neu:'#A9B1B5', neg:'#F2664F' };

function splineCmds(pts) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i-1] || pts[i], p1 = pts[i], p2 = pts[i+1], p3 = pts[i+2] || pts[i+1];
    const c1x = p1[0] + (p2[0]-p0[0])/6, c1y = p1[1] + (p2[1]-p0[1])/6;
    const c2x = p2[0] - (p3[0]-p1[0])/6, c2y = p2[1] - (p3[1]-p1[1])/6;
    out.push(`C ${c1x.toFixed(1)} ${c1y.toFixed(1)} ${c2x.toFixed(1)} ${c2y.toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`);
  }
  return out.join(' ');
}
const sLine = pts => `M ${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)} ${splineCmds(pts)}`;
const sBand = (top, bot) => {
  const br = [...bot].reverse();
  return `${sLine(top)} L ${br[0][0].toFixed(1)} ${br[0][1].toFixed(1)} ${splineCmds(br)} Z`;
};

const SentimentTimeline = ({ data }) => {
  const ref = useRef(null);
  const [w, setW] = useState(936);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const fit = () => setW(el.clientWidth); fit();
    const ro = new ResizeObserver(fit); ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const H = 248, padL = 32, padB = 26, padT = 10, padR = 8;
  const plotW = w - padL - padR, plotH = H - padT - padB;
  const n = data.length;
  // Pick a max that fits the data, rounded up to a nice tick boundary.
  const peak = data.reduce((m,d) => Math.max(m, (d.pos||0) + (d.neu||0) + (d.neg||0)), 0);
  const step = peak <= 8 ? 2 : peak <= 20 ? 5 : peak <= 50 ? 10 : peak <= 100 ? 20 : 50;
  const max = Math.max(step, Math.ceil((peak * 1.1) / step) * step);
  const X = i => padL + (i/(n-1)) * plotW;
  const Y = v => padT + plotH - (v/max) * plotH;
  const base   = data.map((d,i) => [X(i), Y(0)]);
  const posTop = data.map((d,i) => [X(i), Y(d.pos)]);
  const neuTop = data.map((d,i) => [X(i), Y(d.pos + d.neu)]);
  const negTop = data.map((d,i) => [X(i), Y(d.pos + d.neu + d.neg)]);
  const ticks = [];
  for (let t = 0; t <= max; t += step) ticks.push(t);
  const xIdx = data.map((_,i) => i).filter(i => i % 4 === 0);

  return (
    <Card pad={20}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:6 }}>
        <div style={{ fontSize:11.5, fontWeight:600, color:'var(--db-gray-text)', textTransform:'uppercase', letterSpacing:'0.07em' }}>Sentiment timeline · last 30 days</div>
        <div style={{ display:'flex', alignItems:'center', gap:14, fontSize:11.5, color:'var(--db-gray-text)' }}>
          {[['pos','positive'],['neu','neutral'],['neg','negative']].map(([k,l]) => (
            <span key={k} style={{ display:'inline-flex', alignItems:'center', gap:6 }}>
              <span style={{ width:9, height:9, borderRadius:2, background:SENT_FILL[k] }} />{l}
            </span>
          ))}
        </div>
      </div>
      <div ref={ref} style={{ width:'100%' }}>
        <svg width={w} height={H} style={{ display:'block' }}>
          {ticks.map(t => (
            <g key={t}>
              <line x1={padL} y1={Y(t)} x2={w-padR} y2={Y(t)} stroke="var(--db-gray-lines)" strokeWidth="1" opacity={t===0?1:0.6} />
              <text x={padL-8} y={Y(t)+3.5} textAnchor="end" fontSize="10" fill="var(--db-navy-400)" fontFamily="var(--font-mono)">{t}</text>
            </g>
          ))}
          <path d={sBand(posTop, base)}   fill={SENT_FILL.pos} fillOpacity="0.92" />
          <path d={sBand(neuTop, posTop)} fill={SENT_FILL.neu} fillOpacity="0.92" />
          <path d={sBand(negTop, neuTop)} fill={SENT_FILL.neg} fillOpacity="0.92" />
          <path d={sLine(posTop)} fill="none" stroke={SENT_LINE.pos} strokeWidth="1.5" />
          <path d={sLine(negTop)} fill="none" stroke={SENT_LINE.neg} strokeWidth="1.5" />
          {xIdx.map(i => (
            <text key={i} x={X(i)} y={H-9} textAnchor="middle" fontSize="10" fill="var(--db-navy-400)" fontFamily="var(--font-mono)">{data[i].date}</text>
          ))}
        </svg>
      </div>
    </Card>
  );
};

const ReviewCard = ({ rv, replied, onReply }) => {
  const [draft, setDraft] = useState(rv.aiDraft);
  const [editing, setEditing] = useState(false);
  const s = SENT[rv.sentiment];
  return (
    <Card pad={0} style={{ overflow:'hidden' }}>
      <div style={{ padding:'16px 18px' }}>
        <div style={{ display:'flex', alignItems:'center', gap:12 }}>
          <div style={{ width:36, height:36, borderRadius:999, background:'var(--db-oat-medium)', color:'var(--db-navy-800)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:12.5, fontWeight:600, flexShrink:0 }}>{rv.initials}</div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ display:'flex', alignItems:'center', gap:9 }}>
              <span style={{ fontSize:13.5, fontWeight:500, color:'var(--db-navy-800)' }}>{rv.author}</span>
              <Stars n={rv.rating} />
            </div>
            <div style={{ fontSize:11.5, color:'var(--db-gray-text)', marginTop:1 }}>{rv.channel} · {rv.time}</div>
          </div>
          <span style={{ fontSize:11, fontWeight:500, padding:'3px 9px', borderRadius:999, color:s.fg, background:s.bg }}>{s.label}</span>
        </div>
        <p style={{ fontSize:13.5, color:'var(--db-navy-800)', lineHeight:1.55, margin:'12px 0 0' }}>{rv.text}</p>
      </div>

      {replied ? (
        <div style={{ borderTop:'1px solid var(--db-gray-lines)', padding:'14px 18px', background:'var(--db-oat-light)', display:'flex', gap:11 }}>
          <Icon name="reply" size={16} color="var(--db-green-700)" style={{ marginTop:2, flexShrink:0 }} />
          <div style={{ flex:1 }}>
            <div style={{ fontSize:11.5, fontWeight:600, color:'var(--db-green-800)', marginBottom:3 }}>Your reply · sent</div>
            <div style={{ fontSize:13, color:'var(--db-navy-800)', lineHeight:1.5 }}>{draft}</div>
            <div style={{ marginTop:6 }}><LakebaseTag table="review_replies" /></div>
          </div>
        </div>
      ) : rv.needsReply ? (
        <div style={{ borderTop:'1px solid var(--db-gray-lines)', padding:'14px 18px', background:'var(--db-oat-light)' }}>
          <div style={{ display:'flex', alignItems:'center', gap:7, marginBottom:9 }}>
            <Icon name="spark" size={14} color="var(--db-lava-600)" />
            <span style={{ fontSize:11.5, fontWeight:600, color:'var(--db-lava-700)', textTransform:'uppercase', letterSpacing:'0.05em' }}>AI-drafted reply</span>
            <span style={{ fontSize:11, color:'var(--db-gray-text)' }}>· matched to your brand voice, edit before sending</span>
          </div>
          {editing ? (
            <textarea value={draft} onChange={e => setDraft(e.target.value)} rows={4} className="hb-textarea" style={{ width:'100%', boxSizing:'border-box', border:'1px solid var(--db-navy-300)', borderRadius:9, padding:'11px 13px', font:'400 13px/1.55 var(--font-sans)', color:'var(--db-navy-800)', resize:'vertical', outline:'none', background:'#fff' }} />
          ) : (
            <div onClick={() => setEditing(true)} style={{ background:'#fff', border:'1px solid var(--db-gray-lines)', borderRadius:9, padding:'11px 13px', fontSize:13, color:'var(--db-navy-800)', lineHeight:1.55, cursor:'text' }}>{draft}</div>
          )}
          <div style={{ display:'flex', alignItems:'center', gap:9, marginTop:11 }}>
            <Btn size="sm" variant="primary" icon="send" onClick={() => onReply(draft)}>Send reply</Btn>
            <Btn size="sm" variant="ghost" icon="edit" onClick={() => setEditing(e => !e)}>{editing?'Done editing':'Edit'}</Btn>
            <Btn size="sm" variant="quiet" icon="refresh" onClick={() => setDraft(rv.aiDraft)}>Regenerate</Btn>
          </div>
        </div>
      ) : null}
    </Card>
  );
};

const FeedbackView = () => {
  const { reviewsReplied, replyReview } = useApp();
  const [filter, setFilter] = useState('needs');

  // Live theme rollups + sentiment timeline + reviews list.
  const [liveThemes, setLiveThemes] = useState(null);
  const [liveTimeline, setLiveTimeline] = useState(null);
  const [liveReviews, setLiveReviews] = useState(null);
  useEffect(() => {
    fetch('/api/feedback/themes', { credentials: 'include' })
      .then(r => r.ok ? r.json() : null).then(setLiveThemes).catch(() => {});
    fetch('/api/feedback/sentiment-timeline', { credentials: 'include' })
      .then(r => r.ok ? r.json() : null).then(setLiveTimeline).catch(() => {});
    fetch('/api/feedback/reviews?limit=12', { credentials: 'include' })
      .then(r => r.ok ? r.json() : null).then(setLiveReviews).catch(() => {});
  }, []);

  // Map live rows to the ReviewCard shape.
  const reviews = liveReviews
    ? liveReviews.map(r => {
        const fb = r.feedback_id || '';
        const tail = fb.slice(-3) || 'GU';
        const initials = (tail[0] || 'G') + (tail[1] || 'U');
        return {
          id: fb,
          author: `Guest ${tail}`,
          initials: initials.toUpperCase(),
          rating: r.rating,
          channel: (r.channel || '').replace(/^\w/, c => c.toUpperCase()),
          time: r.date,
          sentiment: r.sentiment_label,
          needsReply: !!r.needs_reply,
          text: r.feedback_text,
          aiDraft: r.ai_drafted_reply || '',
        };
      })
    : REVIEWS;

  const needs = reviews.filter(r => r.needsReply && !reviewsReplied.has(r.id)).length;
  const shown = reviews.filter(r => filter==='all' ? true : filter==='needs' ? (r.needsReply && !reviewsReplied.has(r.id)) : r.sentiment==='pos');

  const themeRows = liveThemes
    ? liveThemes.map(t => ({
        theme: t.theme.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        count: t.count_7d,
        dir: t.count_7d >= (t.count_30d / 4) ? 'up' : 'flat',
        level: t.pct_negative_7d >= 50 ? 'warn' : t.pct_negative_7d >= 30 ? 'info' : 'ok',
      }))
    : FEEDBACK_THEMES;
  const sentimentRows = liveTimeline
    ? liveTimeline.map(d => ({ date: d.date.slice(5), pos: d.pos, neu: d.neu, neg: d.neg }))
    : SENTIMENT_30D;
  return (
    <div style={{ flex:1, overflow:'auto', background:'var(--db-oat-light)' }}>
      <div style={{ padding:'28px 32px 40px', maxWidth:1000, margin:'0 auto' }}>
        <PageHead icon="feedback" title="Guest Feedback" sub="Every review across Google, Yelp and the app — clustered into themes, with replies drafted for you." />

        <div style={{ display:'flex', gap:12, marginBottom:18 }}>
          <LaborStat label="Guest score" value="4.3★" foot={<Delta up size={11.5}>+0.1 this week</Delta>} />
          <LaborStat label="NPS" value="41" foot="612 responses" />
          <LaborStat label="Needs reply" value={String(needs)} foot={needs?'awaiting you':'all caught up'} />
          <LaborStat label="Response rate" value="94%" foot="within 24h" />
        </div>

        {/* themes */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12, marginBottom:18 }}>
          {themeRows.map(t => {
            const lv = LEVEL[t.level];
            return (
              <Card key={t.theme} pad="13px 15px">
                <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                  <span style={{ fontSize:20, fontWeight:600, color:'var(--db-navy-800)', fontFamily:'var(--font-mono)' }}>{t.count}</span>
                  <Icon name={t.dir==='up'?'arrowup':'minus'} size={14} color={lv.dot} stroke={2.2} />
                </div>
                <div style={{ fontSize:12.5, color:'var(--db-navy-800)', fontWeight:500, marginTop:4 }}>{t.theme}</div>
              </Card>
            );
          })}
        </div>

        <div style={{ marginBottom:18 }}>
          <SentimentTimeline data={sentimentRows} />
        </div>

        <div style={{ marginBottom:18 }}>
          <AIRec tone="navy" action="See trends" onAction={()=>{}}>
            <strong>Pickup wait times</strong> are the fastest-rising complaint this week — 7 mentions, all clustered at Friday lunch on the mobile-order station. Adding a dedicated runner for the 11:30–1:30 window should clear it.
          </AIRec>
        </div>

        {/* filter */}
        <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:14 }}>
          <h2 style={{ fontSize:16, fontWeight:500, color:'var(--db-navy-800)', margin:0, marginRight:6 }}>Reviews</h2>
          {[['needs',`Needs reply (${needs})`],['all','All'],['pos','Praise']].map(([k,l]) => (
            <button key={k} onClick={() => setFilter(k)} style={{ border:0, cursor:'pointer', fontSize:12.5, fontWeight:500, padding:'5px 12px', borderRadius:999, background: filter===k?'var(--db-navy-800)':'var(--db-oat-medium)', color: filter===k?'#fff':'var(--db-gray-text)' }}>{l}</button>
          ))}
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
          {shown.length ? shown.map(rv => (
            <ReviewCard key={rv.id} rv={rv} replied={reviewsReplied.has(rv.id)} onReply={(text) => replyReview(rv.id, text)} />
          )) : (
            <Card pad={28} style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>
              <Icon name="check" size={18} color="var(--db-green-600)" stroke={2.2} />
              <span style={{ fontSize:13.5, color:'var(--db-green-800)', fontWeight:500 }}>Nothing needs a reply — you're all caught up.</span>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

Object.assign(window, { FeedbackView });
