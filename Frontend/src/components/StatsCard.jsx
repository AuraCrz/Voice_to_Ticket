function StatsCard({ title, value, percentage }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">

      <p className="text-slate-500">
        {title}
      </p>

      <h2 className="text-4xl font-bold text-slate-900 mt-3">
        {value}
      </h2>

      <p className="text-green-500 mt-2 text-sm">
        ↑ {percentage}% esta semana
      </p>

    </div>
  )
}

export default StatsCard