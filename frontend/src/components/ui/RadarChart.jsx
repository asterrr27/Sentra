import { useEffect, useRef } from 'react'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default function RadarChart({ data = {} }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current) return
    if (chartRef.current) chartRef.current.destroy()

    const labels = Object.keys(data)
    const values = Object.values(data)

    chartRef.current = new Chart(ref.current, {
      type: 'radar',
      data: {
        labels,
        datasets: [{
          label: 'Security Score',
          data: values,
          backgroundColor: 'rgba(6,182,212,0.1)',
          borderColor: '#06B6D4',
          borderWidth: 2,
          pointBackgroundColor: '#06B6D4',
          pointBorderColor: '#09090B',
          pointBorderWidth: 2,
          pointRadius: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        animation: { duration: 800, easing: 'easeOutQuart' },
        plugins: {
          legend: { display: false },
        },
        scales: {
          r: {
            min: 0,
            max: 100,
            ticks: {
              stepSize: 25,
              color: 'rgba(255,255,255,0.3)',
              backdropColor: 'transparent',
              font: { size: 10 },
            },
            grid: { color: 'rgba(255,255,255,0.06)' },
            angleLines: { color: 'rgba(255,255,255,0.06)' },
            pointLabels: {
              color: 'rgba(255,255,255,0.6)',
              font: { size: 11, weight: '500' },
            },
          },
        },
      },
    })

    return () => { if (chartRef.current) chartRef.current.destroy() }
  }, [data])

  return <canvas ref={ref} />
}
