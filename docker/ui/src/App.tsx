import React, { useEffect, useMemo, useRef, useState } from 'react'

type Mode = 'WRITE' | 'READ'

function Card({ title, value, accent }: { title: string; value: React.ReactNode; accent?: 'green' | 'red' }) {
  const ring = accent === 'green' ? 'ring-green-400' : accent === 'red' ? 'ring-red-400' : 'ring-gray-200'
  return (
    <div className={`rounded-2xl border p-4 ring-1 ${ring} bg-white shadow-sm`}>
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
    </div>
  )
}

export default function App() {
  const [baseUrl, setBaseUrl] = useState('http://localhost:8000')
  const [durationSec, setDurationSec] = useState(30)
  const [rps, setRps] = useState(20)
  const [mode, setMode] = useState<Mode>('WRITE')
  const [running, setRunning] = useState(false)

  const [startedAt, setStartedAt] = useState<number | null>(null)
  const [finishedAt, setFinishedAt] = useState<number | null>(null)

  const [okCount, setOkCount] = useState(0)
  const [errCount, setErrCount] = useState(0)
  const [latencies, setLatencies] = useState<number[]>([])
  const [lastError, setLastError] = useState<string | null>(null)

  const tickerRef = useRef<number | null>(null)
  const stopTimeoutRef = useRef<number | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  function randomName() {
    const hex = Math.random().toString(16).slice(2, 10)
    return `bench-${hex}`
  }

  function resetStats() {
    setOkCount(0)
    setErrCount(0)
    setLatencies([])
    setLastError(null)
    setStartedAt(null)
    setFinishedAt(null)
  }

  async function fireOnce(signal: AbortSignal) {
    const t0 = performance.now()
    try {
      if (mode === 'WRITE') {
        const r = await fetch(`${baseUrl}/items`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: randomName() }),
          signal,
        })
        if (!r.ok) throw new Error(`POST /items -> ${r.status}`)
      } else {
        const r = await fetch(`${baseUrl}/items`, { signal })
        if (!r.ok) throw new Error(`GET /items -> ${r.status}`)
        await r.json().catch(() => {})
      }
      const t1 = performance.now()
      setOkCount((x) => x + 1)
      setLatencies((prev) => [...prev, t1 - t0])
    } catch (e: any) {
      const t1 = performance.now()
      setErrCount((x) => x + 1)
      setLatencies((prev) => [...prev, t1 - t0])
      setLastError(String(e?.message || e))
    }
  }

  function start() {
    if (running) return
    resetStats()
    setRunning(true)
    const ac = new AbortController()
    abortRef.current = ac
    const started = performance.now()
    setStartedAt(started)

    function tick() {
      if (ac.signal.aborted) return
      const batch = Math.max(1, Math.floor(rps))
      for (let i = 0; i < batch; i++) {
        const delay = Math.floor((i / batch) * 900)
        window.setTimeout(() => fireOnce(ac.signal), delay)
      }
      tickerRef.current = window.setTimeout(tick, 1000)
    }

    tick()
    stopTimeoutRef.current = window.setTimeout(() => stop(), durationSec * 1000)
  }

  function stop() {
    if (!running) return
    abortRef.current?.abort()
    if (tickerRef.current) { window.clearTimeout(tickerRef.current); tickerRef.current = null }
    if (stopTimeoutRef.current) { window.clearTimeout(stopTimeoutRef.current); stopTimeoutRef.current = null }
    setRunning(false)
    setFinishedAt(performance.now())
  }

  useEffect(() => () => stop(), [])

  const elapsedSec = useMemo(() => {
    if (!startedAt) return 0
    const t = finishedAt ?? performance.now()
    return (t - startedAt) / 1000
  }, [startedAt, finishedAt, running])

  function p95(values: number[]) {
    if (!values.length) return 0
    const sorted = [...values].sort((a, b) => a - b)
    const idx = Math.floor(sorted.length * 0.95) - 1
    return sorted[Math.max(0, idx)]
  }

  const computedRps = useMemo(() => {
    const total = okCount + errCount
    return elapsedSec > 0 ? (total / elapsedSec).toFixed(1) : '0.0'
  }, [okCount, errCount, elapsedSec])

  return (
    <div className="min-h-screen bg-white text-black">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-2">DB Load UI</h1>
        <p className="text-sm text-gray-600 mb-6">
          Генерируем нагрузку на БД через REST API приложения. В режиме WRITE выполняются POST /items (INSERT),
          в режиме READ — GET /items (SELECT).
        </p>

        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <label className="block">
            <span className="text-sm font-medium">Base URL</span>
            <input className="mt-1 w-full border rounded-xl px-3 py-2" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} />
          </label>

          <label className="block">
            <span className="text-sm font-medium">Duration (sec)</span>
            <input type="number" min={1} className="mt-1 w-full border rounded-xl px-3 py-2" value={durationSec} onChange={(e) => setDurationSec(Math.max(1, Number(e.target.value)))} />
          </label>

          <label className="block">
            <span className="text-sm font-medium">Target RPS</span>
            <input type="number" min={1} className="mt-1 w-full border rounded-xl px-3 py-2" value={rps} onChange={(e) => setRps(Math.max(1, Number(e.target.value)))} />
          </label>

          <label className="block">
            <span className="text-sm font-medium">Mode</span>
            <select className="mt-1 w-full border rounded-xl px-3 py-2 bg-white" value={mode} onChange={(e) => setMode(e.target.value as Mode)}>
              <option value="WRITE">WRITE — POST /items (INSERT)</option>
              <option value="READ">READ — GET /items (SELECT)</option>
            </select>
          </label>
        </div>

        <div className="flex items-center gap-3 mb-6">
          {!running ? (
            <button onClick={start} className="px-4 py-2 rounded-xl bg-blue-600 text-white">Start</button>
          ) : (
            <button onClick={stop} className="px-4 py-2 rounded-xl bg-gray-700 text-white">Stop</button>
          )}
          <button onClick={resetStats} disabled={running} className="px-4 py-2 rounded-xl border">Reset stats</button>
        </div>

        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <Card title="Elapsed (s)" value={elapsedSec.toFixed(1)} />
          <Card title="RPS (achieved)" value={computedRps} />
          <Card title="P95 latency (ms)" value={p95(latencies).toFixed(1)} />
        </div>

        <div className="grid md:grid-cols-2 gap-4 mb-10">
          <Card title="Success" value={okCount} accent="green" />
          <Card title="Errors" value={errCount} accent="red" />
        </div>

        <div className="mb-4">
          <h2 className="text-lg font-semibold mb-2">Последняя ошибка</h2>
          <pre className="bg-gray-50 border rounded-xl p-3 text-sm overflow-auto min-h-[48px]">{lastError || '—'}</pre>
        </div>
      </div>
    </div>
  )
}
