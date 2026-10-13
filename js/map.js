// GIS Emergency Map Module
class DisasterMapManager {
  constructor(mapElementId, sidebarElementId) {
    this.mapElementId = mapElementId;
    this.sidebarElementId = sidebarElementId;
    this.map = null;
    this.markers = [];
  }

  initMap(incidents, onSelectIncidentCallback) {
    if (!document.getElementById(this.mapElementId)) return;

    // Center map around global view (e.g., Lat 20, Lon 20, Zoom 2)
    this.map = L.map(this.mapElementId, {
      zoomControl: true,
      scrollWheelZoom: true
    }).setView([20, 30], 2);

    // Warm cream-styled tile layer (CartoDB Positron)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(this.map);

    this.renderIncidents(incidents, onSelectIncidentCallback);
  }

  renderIncidents(incidents, onSelectIncidentCallback) {
    if (!this.map) return;

    // Clear existing markers
    this.markers.forEach(m => this.map.removeLayer(m));
    this.markers = [];

    const sidebar = document.getElementById(this.sidebarElementId);
    if (sidebar) sidebar.innerHTML = '';

    incidents.forEach((item, index) => {
      const lat = parseFloat(item.latitude);
      const lng = parseFloat(item.longitude);

      if (isNaN(lat) || isNaN(lng)) return;

      // Color mapping
      let color = '#FF3823'; // Critical
      if (item.allocation_priority === 'High') color = '#FF6B00';
      if (item.allocation_priority === 'Medium') color = '#2D2621';
      if (item.allocation_priority === 'Low') color = '#6E675F';

      // Custom marker icon HTML
      const markerHtml = `
        <div style="
          width: 24px;
          height: 24px;
          background-color: ${color};
          border: 3px solid #FFFFFF;
          border-radius: 50%;
          box-shadow: 0 4px 10px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        ">
        </div>
      `;

      const customIcon = L.divIcon({
        html: markerHtml,
        className: 'custom-map-pin',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      });

      const marker = L.marker([lat, lng], { icon: customIcon }).addTo(this.map);

      const popupContent = `
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; padding: 4px;">
          <div style="font-size: 0.75rem; font-weight: 800; color: #6E675F;">${item.request_id}</div>
          <h4 style="margin: 4px 0 8px 0; font-size: 1rem; color: #1F1A17;">${item.region_name}, ${item.country}</h4>
          <div style="display: flex; gap: 6px; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.75rem; font-weight: 700; background: #F6F3ED; padding: 2px 6px; border-radius: 4px;">${item.disaster_type}</span>
            <span style="font-size: 0.7rem; font-weight: 800; color: #FFF; background: ${color}; padding: 2px 6px; border-radius: 4px; text-transform: uppercase;">${item.allocation_priority}</span>
          </div>
          <p style="font-size: 0.8rem; color: #4A433D; margin-bottom: 10px;">Affected: <strong>${Number(item.population_affected).toLocaleString()}</strong> | Damage: <strong>${item.infrastructure_damage_score}%</strong></p>
          <button onclick="window.inspectDisasterDetail('${item.request_id}')" style="
            width: 100%;
            background-color: #FF3823;
            color: #FFF;
            border: none;
            padding: 8px 12px;
            font-weight: 700;
            font-size: 0.8rem;
            border-radius: 4px;
            cursor: pointer;
          ">Inspect Rationale & Allocate</button>
        </div>
      `;

      marker.bindPopup(popupContent);
      this.markers.push(marker);

      // Add to sidebar list (Screen 5 Sidebar)
      if (sidebar) {
        const itemEl = document.createElement('div');
        itemEl.className = 'map-incident-item';
        itemEl.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-family: monospace; font-weight: 700; font-size: 0.8rem;">${item.request_id}</span>
            <span class="badge-priority ${item.allocation_priority.toLowerCase()}">${item.allocation_priority}</span>
          </div>
          <div style="font-weight: 700; font-size: 0.95rem;">${item.region_name}, ${item.country}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted);">${item.disaster_type} • ${Number(item.population_affected).toLocaleString()} affected</div>
        `;

        itemEl.addEventListener('click', () => {
          this.map.flyTo([lat, lng], 8, { duration: 1.2 });
          marker.openPopup();
          if (onSelectIncidentCallback) onSelectIncidentCallback(item);
        });

        sidebar.appendChild(itemEl);
      }
    });

    if (incidents.length > 0) {
      const bounds = L.latLngBounds(incidents.map(i => [parseFloat(i.latitude), parseFloat(i.longitude)]));
      this.map.fitBounds(bounds, { padding: [50, 50] });
    }
  }
}

window.DisasterMapManager = DisasterMapManager;
