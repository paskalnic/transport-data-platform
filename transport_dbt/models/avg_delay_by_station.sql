SELECT
    station_name,
    AVG(avg_delay_minutes) as avg_delay,
    SUM(total_trains) as total_trains
FROM transport-data-platform-2026.transport_data.departures_prod
GROUP BY station_name
ORDER BY avg_delay DESC
