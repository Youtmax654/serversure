import { useState, useEffect } from "react"
import axios from "axios"

export const useMetrics = (ipAddress) => {
    const DEFAULT_IP = "localhost"
    const protocol = ipAddress.includes('http') ? '' : 'http://'
    const baseUrl = `${protocol}${ipAddress || DEFAULT_IP}:8000`

    const [last, setLast] = useState(null)
    const [history, setHistory] = useState([])
    const [alerts, setAlerts] = useState([])
    const [photos, setPhotos] = useState([])
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        try {
            console.log(`Fetching from ${baseUrl}`)
            const [lastRes, histRes, alertsRes] = await Promise.all([
                axios.get(`${baseUrl}/api/sensors/last`),
                axios.get(`${baseUrl}/api/sensors/history?limit=20`),
                axios.get(`${baseUrl}/api/alerts`),
            ])

            setLast(lastRes.data)
            setHistory(histRes.data)
            setAlerts(alertsRes.data)

            // Attempt to infer photos from alerts or fetch separate endpoint if exists
            // Assuming alerts might contain photo filenames, or we fetch /api/photos
            // For now, let's try to fetch /api/photos just in case
            try {
                // This endpoint is speculative based on common patterns, but not mandated by user
                // We will default to empty array if 404
                const photoRes = await axios.get(`${baseUrl}/api/photos`)
                setPhotos(photoRes.data)
            } catch (e) {
                // Fallback: If alerts have photos, extract them
                const alertPhotos = alertsRes.data
                    .filter(a => a.photo || a.filename || a.image)
                    .map(a => a.photo || a.filename || a.image)

                // If alert object has no photo field, we might need another strategy.
                // But let's leave empty for now if no endpoint.
                setPhotos(alertPhotos)
            }

            setError(null)
        } catch (err) {
            console.error("Error fetching data:", err)
            setError(err)
            // Mock data for demo purposes if fetch fails (so user sees UI)
            if (!last) {
                setLast({ temperature: 24, humidity: 45, luminosity: 300, timestamp: new Date().toISOString() })
                setHistory(Array.from({ length: 20 }, (_, i) => ({
                    timestamp: new Date(Date.now() - i * 5000).toISOString(),
                    temperature: 20 + Math.random() * 10,
                    humidity: 40 + Math.random() * 10,
                    luminosity: 200 + Math.random() * 200
                })).reverse())
                setAlerts([
                    { timestamp: new Date().toISOString(), type: 'ALERT', distance: 10, message: "Motion Detected" }
                ])
                setPhotos([
                    'https://images.unsplash.com/photo-1550751827-4bd374c3f58b',
                    'https://images.unsplash.com/photo-1518770660439-4636190af475',
                    'https://images.unsplash.com/photo-1551288049-bebda4e38f71',
                    'https://images.unsplash.com/photo-1563089145-599997674d42'
                ])
            }
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData() // Initial fetch
        const interval = setInterval(fetchData, 5000)
        return () => clearInterval(interval)
    }, [ipAddress])

    return { last, history, alerts, photos, error, loading }
}
