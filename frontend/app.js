/* ==========================================================================
   Urban Road Encroachment Detection System
   Enterprise Decision-Support Dashboard Application Logic
   ========================================================================== */

let map = null;
let geojsonLayers = {};
let allCases = [];
let allProperties = [];

window.mapLayers = {};
window.baseLayers = {};
window.encroachmentPolygons = {};
window.vectorEncroachmentPolygons = {};
let vectorMap = null;

document.addEventListener("DOMContentLoaded", () => {
    loadSummary();
    loadCases();
    loadProperties();
    initMap();
    loadPredictionsGallery();
});

// Tab Switcher Logic
function switchTab(tabId) {
    document.querySelectorAll(".tab-item").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

    const selectedTabItem = Array.from(document.querySelectorAll(".tab-item")).find(t => {
        const onclickAttr = t.getAttribute("onclick");
        return onclickAttr && onclickAttr.includes(`'${tabId}'`);
    });
    if (selectedTabItem) selectedTabItem.classList.add("active");

    const targetContent = document.getElementById(`tab-${tabId}`);
    if (targetContent) targetContent.classList.add("active");

    if (tabId === "gis-map") {
        if (map) setTimeout(() => map.invalidateSize(), 200);
        if (vectorMap) setTimeout(() => vectorMap.invalidateSize(), 200);
    }
}

// Fetch Summary Cards Data
async function loadSummary() {
    try {
        const res = await fetch("/api/summary");
        const data = await res.json();

        const elStudy = document.getElementById("sum-study-area");
        if (elStudy) elStudy.innerText = data.study_area || "Synthetic Colony";

        const elRoad = document.getElementById("sum-road-id");
        if (elRoad) elRoad.innerText = data.road_id || "Road R-001";

        const elProp = document.getElementById("sum-properties");
        if (elProp) elProp.innerText = data.properties_count || "10";

        const elRow = document.getElementById("sum-row-width");
        if (elRow) elRow.innerText = `${data.legal_row_width_m || 9.00} m`;

        const elCw = document.getElementById("sum-carriageway");
        if (elCw) elCw.innerText = `${data.existing_carriageway_m || 6.00} m`;

        const elDet = document.getElementById("sum-detections");
        if (elDet) elDet.innerText = data.physical_detections_count || "2";

        const elCases = document.getElementById("sum-cases");
        if (elCases) elCases.innerText = data.potential_encroachment_cases_count || "2";

        const elArea = document.getElementById("sum-area");
        if (elArea) elArea.innerText = `${data.potential_encroachment_area_sqm || 9.60} m²`;
    } catch (e) {
        console.error("Failed to load summary:", e);
    }
}

// Fetch Encroachment Cases Table Data
async function loadCases() {
    try {
        const res = await fetch("/api/encroachments");
        const data = await res.json();
        allCases = data.cases || [];
        renderCasesTable(allCases);
    } catch (e) {
        console.error("Failed to load encroachment cases:", e);
    }
}

// Fetch Properties Table Data
async function loadProperties() {
    try {
        const res = await fetch("/api/properties");
        const data = await res.json();
        allProperties = data.properties || [];
        renderPropertyTable(allProperties);
    } catch (e) {
        console.error("Failed to load property parcels:", e);
    }
}

function renderPropertyTable(props) {
    const tbody = document.getElementById("property-table-body");
    if (!tbody) return;

    tbody.innerHTML = props.map(p => {
        const hasCase = p.parcel_id === 'P-07' || p.parcel_id === 'P-08';
        const parts = (p.address_synthetic || "").split(",");
        const houseNo = parts[0] ? parts[0].trim() : p.parcel_id;
        const cleanName = (p.owner_name_synthetic || "").replace(" (Synthetic)", "").trim();

        const badgeHtml = hasCase
            ? '<span class="badge badge-high">Potential Encroachment (Field Verification Required)</span>'
            : '<span class="badge badge-permissible">Permissible (Within Private Setback)</span>';

        return `
            <tr>
                <td><strong>${houseNo}</strong> (${p.parcel_id})</td>
                <td>${cleanName}</td>
                <td>${p.address_synthetic}</td>
                <td class="td-num">${p.area_sqm.toFixed(1)} m²</td>
                <td>Road R-001 Frontage</td>
                <td>${badgeHtml}</td>
            </tr>
        `;
    }).join("");
}

// Render Cases Table with Enterprise Formatting
function renderCasesTable(cases) {
    const tbody = document.getElementById("table-cases-body");
    if (!tbody) return;

    if (cases.length === 0) {
        tbody.innerHTML = `<tr><td colspan="12" style="text-align:center; color:var(--text-secondary); padding: 20px;">No encroachment cases match the selected filter criteria.</td></tr>`;
        return;
    }

    tbody.innerHTML = cases.map(c => {
        const isBenchmark = c.data_provenance && c.data_provenance.includes("BENCHMARK");
        const provBadge = isBenchmark
            ? '<span class="badge badge-ref">Synthetic Benchmark</span>'
            : '<span class="badge badge-yolo">YOLO Prediction</span>';

        const confText = isBenchmark
            ? `<span title="Synthetic ground-truth verification control" style="color:var(--text-secondary);">100% (Ref)</span>`
            : `${(c.confidence * 100).toFixed(1)}%`;

        return `
            <tr>
                <td><strong>${c.case_id}</strong></td>
                <td><strong>${c.parcel_id}</strong></td>
                <td>${c.structure_concept}</td>
                <td>${provBadge}</td>
                <td class="td-num"><strong>${c.area_sqm.toFixed(2)} m²</strong></td>
                <td class="td-num">${c.max_projection_m.toFixed(2)} m</td>
                <td class="td-num">${c.frontage_m.toFixed(2)} m</td>
                <td><code>${c.chainage_str}</code></td>
                <td class="td-num">${confText}</td>
                <td><span class="badge badge-${c.severity.toLowerCase()}">${c.severity}</span></td>
                <td><strong style="color:var(--danger); font-size:11.5px;">${c.action_required}</strong></td>
                <td>
                    <div style="display:flex; gap:6px;">
                        <button class="btn btn-secondary btn-sm" onclick="openCaseModal('${c.case_id}')">Inspect</button>
                        <a href="/api/report/${c.case_id}" target="_blank" class="btn btn-primary btn-sm" style="text-decoration:none;">Notice</a>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function applyFilters() {
    const searchEl = document.getElementById("filter-search");
    const search = searchEl ? searchEl.value.toLowerCase().trim() : "";
    const prop = document.getElementById("filter-property") ? document.getElementById("filter-property").value : "";
    const sev = document.getElementById("filter-severity") ? document.getElementById("filter-severity").value : "";
    const prov = document.getElementById("filter-provenance") ? document.getElementById("filter-provenance").value : "";

    const filtered = allCases.filter(c => {
        const matchSearch = !search ||
            c.case_id.toLowerCase().includes(search) ||
            c.parcel_id.toLowerCase().includes(search) ||
            c.structure_concept.toLowerCase().includes(search);
        const matchProp = !prop || c.parcel_id === prop;
        const matchSev = !sev || c.severity === sev;
        const matchProv = !prov || (c.data_provenance && c.data_provenance.includes(prov));
        return matchSearch && matchProp && matchSev && matchProv;
    });

    renderCasesTable(filtered);
}

// Case Modal Details Popup
function openCaseModal(caseId) {
    const c = allCases.find(item => item.case_id === caseId || (caseId === "E-01" && item.parcel_id === "P-07") || (caseId === "E-02" && item.parcel_id === "P-08"));
    if (!c) return;

    const modalBody = document.getElementById("modal-body-content");
    document.getElementById("modal-case-title").innerText = `Encroachment Case Detail: ${c.case_id}`;

    const isBenchmark = c.data_provenance && c.data_provenance.includes("BENCHMARK");
    const confDisplay = isBenchmark
        ? "100% (Synthetic GIS Reference Benchmark Control)"
        : `${(c.confidence * 100).toFixed(2)}% (YOLOv8n-seg Instance Segmentation)`;

    modalBody.innerHTML = `
        <div style="font-size: 13px; line-height: 1.6;">
            <div style="background-color: var(--danger-bg); border: 1px solid var(--danger-border); color: var(--danger); padding: 12px 14px; border-radius: 4px; font-weight: 600; margin-bottom: 16px;">
                STATUS: ${c.status}<br>
                REQUIRED ACTION: ${c.action_required}
            </div>

            <table class="data-table" style="margin-bottom: 16px;">
                <tbody>
                    <tr><th style="width: 35%;">Case Reference ID</th><td><strong>${c.case_id}</strong></td></tr>
                    <tr><th>Data Provenance</th><td><span class="badge badge-ref">${c.data_provenance}</span></td></tr>
                    <tr><th>Associated Property</th><td><strong>${c.parcel_id}</strong></td></tr>
                    <tr><th>Road ROW Corridor</th><td>${c.row_id} (Road R-001)</td></tr>
                    <tr><th>Structure Concept</th><td>${c.structure_concept}</td></tr>
                    <tr><th>Confidence Metric</th><td>${confDisplay}</td></tr>
                    <tr><th>Encroached Area</th><td><strong style="color:var(--danger); font-size:14px;">${c.area_sqm.toFixed(2)} m²</strong></td></tr>
                    <tr><th>Max Projection Depth</th><td><strong>${c.max_projection_m.toFixed(2)} m</strong> into Right-of-Way</td></tr>
                    <tr><th>Corridor Frontage Width</th><td><strong>${c.frontage_m.toFixed(2)} m</strong> along property boundary</td></tr>
                    <tr><th>Centerline Chainage</th><td><strong>${c.chainage_str}</strong> (${c.chainage_m.toFixed(1)} meters from datum)</td></tr>
                    <tr><th>Engineering Severity</th><td><span class="badge badge-${c.severity.toLowerCase()}">${c.severity}</span></td></tr>
                </tbody>
            </table>

            <div style="margin: 16px 0; display: flex; gap: 10px;">
                <a href="/api/report/${c.case_id}" target="_blank" class="btn btn-primary" style="flex: 1; text-align: center; text-decoration: none; padding: 9px 14px; font-size: 13px;">
                    Generate Municipal Notice &amp; Technical Sheet
                </a>
            </div>

            <div style="font-size: 11.5px; color: var(--text-secondary); border-top: 1px solid var(--border); padding-top: 10px;">
                Mandatory Disclosure: ${c.disclaimer}
            </div>
        </div>
    `;

    document.getElementById("case-modal").classList.add("active");
}

function closeModal() {
    document.getElementById("case-modal").classList.remove("active");
}

// Collapsible Layer Group Controls
function toggleLayerGroup(groupId) {
    const el = document.getElementById(groupId);
    const toggleEl = document.getElementById(`${groupId}-toggle`);
    if (!el) return;
    if (el.style.display === "none") {
        el.style.display = "flex";
        if (toggleEl) toggleEl.innerText = "−";
    } else {
        el.style.display = "none";
        if (toggleEl) toggleEl.innerText = "+";
    }
}

// Custom Layer Toggles for Sidebar
function toggleMapLayer(layerKey) {
    if (!window.mapLayers || !window.mapLayers[layerKey] || !map) return;
    const chk = document.getElementById(`chk-${layerKey}`);
    if (chk && chk.checked) {
        map.addLayer(window.mapLayers[layerKey]);
    } else {
        map.removeLayer(window.mapLayers[layerKey]);
    }
}

function switchBaseLayer(layerKey) {
    if (!window.baseLayers || !map) return;
    Object.values(window.baseLayers).forEach(l => {
        if (l && map.hasLayer(l)) map.removeLayer(l);
    });

    if (layerKey === "clean" && window.baseLayers.clean) {
        map.addLayer(window.baseLayers.clean);
    } else if (layerKey === "annotated" && window.baseLayers.annotated) {
        map.addLayer(window.baseLayers.annotated);
    }
}

// Primary Interactive Leaflet Map Initialization
async function initMap() {
    const mapElement = document.getElementById("leaflet-map");
    if (!mapElement) return;

    const imgW = 1024;
    const imgH = 723;
    const imgBounds = [[0, 0], [imgH, imgW]];

    map = L.map('leaflet-map', {
        crs: L.CRS.Simple,
        minZoom: -1,
        maxZoom: 3,
        zoomSnap: 0.25,
        zoomDelta: 0.5
    });

    map.fitBounds(imgBounds);

    // Base Layers
    const baseDroneClean = L.imageOverlay('/dataset/gis_outputs/original_drone_survey.jpg', imgBounds, {
        opacity: 1.0,
        attribution: 'UAV Aerial Drone Survey (1024x723, Unmodified)'
    }).addTo(map);

    const baseDroneAnnotated = L.imageOverlay('/dataset/gis_outputs/encroachment_reference_survey.jpg', imgBounds, {
        opacity: 0.9,
        attribution: 'UAV Aerial Drone Survey (Reference Ground-Truth Markings)'
    });

    const baseNeutralCanvas = L.layerGroup();

    window.baseLayers = {
        clean: baseDroneClean,
        annotated: baseDroneAnnotated,
        neutral: baseNeutralCanvas
    };

    // Overlays
    const buildingFootprintsLayer = L.layerGroup().addTo(map);
    const parcelsLayer = L.layerGroup().addTo(map);
    const rowLayer = L.layerGroup().addTo(map);
    const footpathsLayer = L.layerGroup().addTo(map);
    const carriagewayLayer = L.layerGroup().addTo(map);
    const centerlineLayer = L.layerGroup().addTo(map);
    const chainageLayer = L.layerGroup().addTo(map);
    const benchmarkLayer = L.layerGroup().addTo(map);
    const yoloLayer = L.layerGroup().addTo(map);

    window.mapLayers = {
        footprints: buildingFootprintsLayer,
        parcels: parcelsLayer,
        row: rowLayer,
        footpaths: footpathsLayer,
        carriageway: carriagewayLayer,
        centerline: centerlineLayer,
        benchmarks: benchmarkLayer,
        yolo: yoloLayer
    };

    try {
        // 1. Building Footprints Layer
        const resB = await fetch("/api/layers/05_BUILDING_FOOTPRINTS_IMAGE");
        const dataB = await resB.json();
        L.geoJSON(dataB, {
            style: { color: "#1e3a8a", fillColor: "#3b82f6", fillOpacity: 0.35, weight: 1.8 },
            onEachFeature: (feat, layer) => {
                const props = feat.properties;
                layer.bindTooltip(`<strong>${props.building_id}</strong><br><small>${props.name}</small>`, {
                    direction: "center",
                    className: "property-label",
                    permanent: false
                });
                layer.bindPopup(`
                    <div style="font-size:12px; line-height:1.5;">
                        <span class="badge badge-ref" style="margin-bottom:4px; display:inline-block;">PHYSICAL STRUCTURE FOOTPRINT</span>
                        <strong style="display:block; font-size:13px; color:#1e3a8a; margin-bottom:4px;">${props.name}</strong>
                        <strong>Building ID:</strong> ${props.building_id}<br>
                        <strong>Associated Parcel:</strong> ${props.parcel_id}<br>
                        <strong>Structure Type:</strong> ${props.structure_type}<br>
                        <strong>Data Provenance:</strong> ${props.data_provenance}<br>
                        <strong>Setback from ROW:</strong> ${props.setback_from_row_m.toFixed(2)} m<br>
                        <strong>Status:</strong> <span style="color:#15803d; font-weight:600;">${props.status}</span>
                    </div>
                `);
            }
        }).addTo(buildingFootprintsLayer);

        // 2. Cadastral Property Boundary Layer
        const resP = await fetch("/api/layers/01_PROPERTY_BOUNDARY_IMAGE");
        const dataP = await resP.json();
        L.geoJSON(dataP, {
            style: { color: "#0284c7", fillColor: "#e0f2fe", fillOpacity: 0.08, weight: 1.8, dashArray: "4, 4" },
            onEachFeature: (feat, layer) => {
                const props = feat.properties;
                const hNo = props.house_no || (props.address_synthetic ? props.address_synthetic.split(',')[0].trim() : props.parcel_id);
                const cleanName = (props.owner_name_synthetic || "").replace(" (Synthetic)", "").trim();
                layer.bindTooltip(`<strong>${hNo} (${props.parcel_id})</strong><br><small>${cleanName}</small>`, {
                    direction: "center",
                    className: "property-label",
                    permanent: false
                });
                layer.on('click', () => {
                    showParcelDetail(props);
                });
            }
        }).addTo(parcelsLayer);

        // 3. Road ROW Layer
        const resR = await fetch("/api/layers/02_ROAD_ROW_IMAGE");
        const dataR = await resR.json();
        L.geoJSON(dataR, {
            style: { color: "#ca8a04", fillColor: "transparent", weight: 2.2, dashArray: "6, 6" },
            onEachFeature: (feat, layer) => {
                layer.bindPopup(`<strong style="color:#ca8a04;">Legal Road ROW (9.00 m Corridor)</strong><br>Controlling statutory public road corridor.`);
            }
        }).addTo(rowLayer);

        // 4. Footpaths Layer
        const resSM = await fetch("/api/layers/06_SIDE_MARGINS_IMAGE");
        const dataSM = await resSM.json();
        L.geoJSON(dataSM, {
            style: { color: "#0891b2", fillColor: "#cffafe", fillOpacity: 0.25, weight: 2.0, dashArray: "4, 4" },
            onEachFeature: (feat, layer) => {
                const props = feat.properties;
                layer.bindTooltip(`<strong>${props.name}</strong><br><small>Width: ${props.width_m.toFixed(2)} m</small>`, {
                    direction: "center",
                    className: "property-label",
                    permanent: false
                });
                layer.bindPopup(`
                    <div style="font-size:12px; line-height:1.5;">
                        <span class="badge badge-ref" style="margin-bottom:4px; display:inline-block;">FOOTPATH MARGIN</span>
                        <strong style="display:block; font-size:13px; color:#0891b2; margin-bottom:4px;">${props.name}</strong>
                        <strong>Margin ID:</strong> ${props.margin_id}<br>
                        <strong>Corridor Side:</strong> ${props.corridor_side}<br>
                        <strong>Design Width:</strong> ${props.width_m.toFixed(2)} m<br>
                        <strong>Surface Type:</strong> ${props.surface_type}
                    </div>
                `);
            }
        }).addTo(footpathsLayer);

        // 5. Existing Carriageway Layer
        const resCW = await fetch("/api/layers/04_EXISTING_CARRIAGEWAY_IMAGE");
        const dataCW = await resCW.json();
        L.geoJSON(dataCW, {
            style: { color: "#dc2626", fillColor: "#64748b", fillOpacity: 0.25, weight: 2.2 },
            onEachFeature: (feat, layer) => {
                layer.bindPopup(`<strong style="color:#dc2626;">Paved Carriageway (6.00 m Roadway)</strong><br>Dedicated vehicular transit corridor.`);
            }
        }).addTo(carriagewayLayer);

        // 6. Centerline Layer
        const resCL = await fetch("/api/layers/03_ROAD_CENTERLINE_IMAGE");
        const dataCL = await resCL.json();
        L.geoJSON(dataCL, {
            style: { color: "#16a34a", weight: 2.0, dashArray: "5, 5" }
        }).addTo(centerlineLayer);

        // 7. Chainage Markers Layer
        const resCH = await fetch("/api/layers/09_CHAINAGE_IMAGE");
        const dataCH = await resCH.json();
        L.geoJSON(dataCH, {
            pointToLayer: (feat, latlng) => L.circleMarker(latlng, {
                radius: 4,
                color: "#0f172a",
                fillColor: "#ffffff",
                fillOpacity: 1,
                weight: 2
            }),
            onEachFeature: (feat, layer) => {
                layer.bindTooltip(`Station: ${feat.properties.chainage_str}`, { direction: "left" });
            }
        }).addTo(chainageLayer);

        // 8. Synthetic Reference Encroachments Layer
        const resE = await fetch("/api/layers/08_POTENTIAL_ENCROACHMENT_IMAGE");
        const dataE = await resE.json();
        L.geoJSON(dataE, {
            style: { color: "#b91c1c", fillColor: "#dc2626", fillOpacity: 0.65, weight: 2.5 },
            onEachFeature: (feat, layer) => {
                const props = feat.properties;
                const isE01 = props.benchmark_id === 'E-01' || props.case_id.includes('4A8C');
                const labelTitle = isE01 ? "E-01 [Ref Benchmark]" : "E-02 [Ref Benchmark]";
                const caseKey = isE01 ? "ENC-4A8C13E2" : "ENC-FFF7E662";

                window.encroachmentPolygons[caseKey] = layer;

                layer.bindTooltip(
                    `<div style="font-weight:600;">${labelTitle}</div><div style="font-size:10px;">${props.structure_concept.split('/')[0]} (${props.parcel_id})<br>Area: ${props.area_sqm.toFixed(2)} m² | Proj: ${props.max_projection_m.toFixed(2)}m</div>`,
                    { permanent: true, direction: "right", className: "encroachment-tooltip", offset: [10, 0] }
                );

                layer.bindPopup(`
                    <div style="font-size:12px; line-height:1.5;">
                        <span class="badge badge-ref" style="margin-bottom:4px; display:inline-block;">SYNTHETIC GIS BENCHMARK</span>
                        <strong style="color:#b91c1c; font-size:13px; display:block; margin-bottom:4px;">
                            ${isE01 ? 'Case E-01 (Top / North)' : 'Case E-02 (Bottom / South)'}
                        </strong>
                        <strong>Property:</strong> ${props.parcel_id}<br>
                        <strong>Structure:</strong> ${props.structure_concept}<br>
                        <strong>Encroached Area:</strong> <span style="color:#b91c1c; font-weight:bold;">${props.area_sqm.toFixed(2)} m²</span><br>
                        <strong>Max Projection:</strong> ${props.max_projection_m.toFixed(2)} m into ROW<br>
                        <strong>Frontage:</strong> ${props.frontage_m.toFixed(2)} m | <strong>Chainage:</strong> ${props.chainage_str}<br>
                        <div style="margin-top:8px;">
                            <button onclick="openCaseModal('${props.case_id}')" class="btn btn-primary btn-sm">Inspect Full Case</button>
                        </div>
                    </div>
                `);

                layer.on('click', () => {
                    showBenchmarkDetail(props);
                });
            }
        }).addTo(benchmarkLayer);

        // 9. YOLOv8n-seg Predictions Layer
        const resY = await fetch("/api/layers/10_YOLO_PREDICTIONS_IMAGE");
        const dataY = await resY.json();
        L.geoJSON(dataY, {
            style: (feat) => {
                const zone = feat.properties.corridor_zone;
                if (zone === "BETWEEN_PAVED_ROAD_AND_FOOTPATH") {
                    return { color: "#dc2626", fillColor: "#ea580c", fillOpacity: 0.65, weight: 2.8, dashArray: "3, 3" };
                }
                if (zone === "FOOTPATH") {
                    return { color: "#b91c1c", fillColor: "#f97316", fillOpacity: 0.60, weight: 2.6 };
                }
                if (zone === "PAVED_ROAD") {
                    return { color: "#991b1b", fillColor: "#dc2626", fillOpacity: 0.70, weight: 3.0 };
                }
                const cid = feat.properties.class_id;
                if (cid === 0) return { color: "#6b21a8", fillColor: "#9333ea", fillOpacity: 0.35, weight: 1.8 };
                if (cid === 7) return { color: "#334155", fillColor: "#64748b", fillOpacity: 0.35, weight: 1.8 };
                return { color: "#0e7490", fillColor: "#06b6d4", fillOpacity: 0.35, weight: 1.8 };
            },
            onEachFeature: (feat, layer) => {
                const props = feat.properties;
                const isCorridorEncroachment = (props.corridor_zone === 'BETWEEN_PAVED_ROAD_AND_FOOTPATH' || props.corridor_zone === 'FOOTPATH' || props.corridor_zone === 'PAVED_ROAD');

                const zoneBadge = props.corridor_zone === 'BETWEEN_PAVED_ROAD_AND_FOOTPATH'
                    ? '<span class="badge badge-high">Encroachment: Between Road & Footpath</span>'
                    : (props.corridor_zone === 'FOOTPATH'
                        ? '<span class="badge badge-critical">Footpath Encroachment</span>'
                        : (props.corridor_zone === 'PAVED_ROAD'
                            ? '<span class="badge badge-critical">Carriageway Encroachment</span>'
                            : '<span class="badge badge-permissible">Private Parcel</span>'));

                layer.bindTooltip(
                    `<div style="font-weight:600;">${props.class_name}</div>${zoneBadge}<div style="font-size:10px; color:#64748b; margin-top:2px;">Conf: ${(props.confidence * 100).toFixed(1)}% | YOLOv8n-seg</div>`,
                    { permanent: false, direction: "top", className: "yolo-tooltip" }
                );
                layer.bindPopup(`
                    <div style="font-size:12px; line-height:1.5;">
                        <span class="badge badge-yolo" style="margin-bottom:4px; display:inline-block;">YOLO PHYSICAL DETECTION</span>
                        ${zoneBadge}
                        <strong style="display:block; font-size:13px; color:#0f172a; margin-top:4px; margin-bottom:4px;">${props.detection_id}: ${props.class_name}</strong>
                        <strong>Corridor Zone:</strong> <span style="font-weight:600; color:${isCorridorEncroachment ? '#b91c1c' : '#15803d'};">${props.corridor_zone || 'PRIVATE_PROPERTY'}</span><br>
                        <strong>Description:</strong> ${props.corridor_zone_desc || ''}<br>
                        <strong>GIS Evaluation:</strong> <strong style="color:${isCorridorEncroachment ? '#b91c1c' : '#15803d'};">${isCorridorEncroachment ? 'POTENTIAL ROAD ROW ENCROACHMENT' : 'WITHIN PERMISSIBLE BOUNDARY'}</strong><br>
                        <strong>Confidence:</strong> ${(props.confidence * 100).toFixed(2)}%<br>
                        <strong>Action Required:</strong> <span style="font-weight:600; color:var(--danger);">${isCorridorEncroachment ? 'FIELD VERIFICATION REQUIRED' : 'NO ACTION REQUIRED'}</span>
                    </div>
                `);
                layer.on('click', () => {
                    showYoloDetail(props);
                });
            }
        }).addTo(yoloLayer);

        // Initialize Vector CAD Map for Dual/Vector Mode
        initVectorMap();

        // Populate Sidebar Overview Immediately
        renderDefaultSidebar();

    } catch (e) {
        console.error("Failed to load map layers:", e);
    }
}

// Secondary Vector CAD Map (Metric Coordinates)
async function initVectorMap() {
    const vectorElement = document.getElementById("vector-map");
    if (!vectorElement) return;

    vectorMap = L.map('vector-map', {
        crs: L.CRS.Simple,
        minZoom: -2,
        maxZoom: 3
    });

    vectorMap.fitBounds([[-5, -5], [40, 55]]);

    const parcelsLayer = L.layerGroup().addTo(vectorMap);
    const rowLayer = L.layerGroup().addTo(vectorMap);
    const carriagewayLayer = L.layerGroup().addTo(vectorMap);
    const centerlineLayer = L.layerGroup().addTo(vectorMap);
    const chainageLayer = L.layerGroup().addTo(vectorMap);
    const encroachmentLayer = L.layerGroup().addTo(vectorMap);

    try {
        const resP = await fetch("/api/layers/01_PROPERTY_BOUNDARY");
        L.geoJSON(await resP.json(), {
            style: { color: "#0284c7", fillColor: "#e0f2fe", fillOpacity: 0.45, weight: 1.5 },
            onEachFeature: (feat, layer) => {
                const props = feat.properties;
                const pid = props.parcel_id || "";
                const hNo = props.house_no || (props.address_synthetic ? props.address_synthetic.split(',')[0].trim() : "");
                layer.bindPopup(`
                    <div style="font-size:12px; line-height:1.5;">
                        <strong style="font-size:13px; color:#0f172a;">${pid}: ${hNo}</strong><br>
                        <strong>Owner:</strong> ${props.owner_name_synthetic || 'N/A'}<br>
                        <strong>Structure:</strong> ${props.structure_type || 'Residential'}<br>
                        <strong>Plot Area:</strong> ${props.area_sqm || 0} m²<br>
                        <strong>Side:</strong> ${props.corridor_side || ''} Corridor
                    </div>
                `);
                layer.on("click", () => showPropertyDetail(props));
            }
        }).addTo(parcelsLayer);

        const resR = await fetch("/api/layers/02_ROAD_ROW");
        L.geoJSON(await resR.json(), {
            style: { color: "#b91c1c", fillColor: "#fef2f2", fillOpacity: 0.25, weight: 2, dashArray: "5, 5" }
        }).addTo(rowLayer);

        const resCW = await fetch("/api/layers/04_EXISTING_CARRIAGEWAY");
        L.geoJSON(await resCW.json(), {
            style: { color: "#475569", fillColor: "#cbd5e1", fillOpacity: 0.55, weight: 1 }
        }).addTo(carriagewayLayer);

        const resCL = await fetch("/api/layers/03_ROAD_CENTERLINE");
        L.geoJSON(await resCL.json(), {
            style: { color: "#ca8a04", weight: 2.2, dashArray: "4, 4" }
        }).addTo(centerlineLayer);

        const resCH = await fetch("/api/layers/09_CHAINAGE");
        L.geoJSON(await resCH.json(), {
            pointToLayer: (feat, latlng) => L.circleMarker(latlng, { radius: 4, color: "#0f172a", fillColor: "#0f172a", fillOpacity: 1 })
        }).addTo(chainageLayer);

        const resE = await fetch("/api/layers/08_POTENTIAL_ENCROACHMENT");
        L.geoJSON(await resE.json(), {
            style: { color: "#b91c1c", fillColor: "#dc2626", fillOpacity: 0.90, weight: 2 },
            onEachFeature: (feat, layer) => {
                const props = feat.properties;
                const isE01 = props.case_id.includes('4A8C') || props.parcel_id === 'P-07';
                window.vectorEncroachmentPolygons[isE01 ? "ENC-4A8C13E2" : "ENC-FFF7E662"] = layer;
                const encName = isE01 ? 'E-01' : 'E-02';
                // Only mention encroachment name without cluttering the parcels
                layer.bindTooltip(`${encName}: ${props.area_sqm.toFixed(2)} m²`, { permanent: true, direction: "right" });
                layer.bindPopup(`
                    <div style="font-size:12px; line-height:1.5;">
                        <span class="badge badge-high" style="margin-bottom:4px; display:inline-block;">ACTIVE ENCROACHMENT VIOLATION</span>
                        <strong style="display:block; font-size:13px; color:#b91c1c; margin-top:4px;">${encName} (${props.parcel_id}): ${props.class_name || 'Encroachment'}</strong>
                        <strong>Parcel:</strong> ${props.parcel_id} (${isE01 ? 'H.No. 12-1-4' : 'H.No. 12-1-6'})<br>
                        <strong>Encroached Area:</strong> <strong style="color:var(--danger);">${props.area_sqm.toFixed(2)} m²</strong><br>
                        <strong>Frontage:</strong> ${props.frontage_m} m | <strong>Projection:</strong> ${props.max_projection_m} m<br>
                        <strong>Chainage:</strong> ${props.chainage_str} | <strong>Status:</strong> ${props.action_required || 'FIELD VERIFICATION REQUIRED'}
                    </div>
                `);
                layer.on("click", () => {
                    focusEncroachment(isE01 ? "ENC-4A8C13E2" : "ENC-FFF7E662");
                });
            }
        }).addTo(encroachmentLayer);

    } catch (e) {
        console.error("Failed to load vector map layers:", e);
    }
}

// Render Default Encroachment Results Overview in Sidebar
function renderDefaultSidebar() {
    const detailBox = document.getElementById("sidebar-detail");
    const resetBtn = document.getElementById("btn-reset-sidebar");
    if (resetBtn) resetBtn.style.display = "none";
    if (!detailBox) return;

    detailBox.innerHTML = `
        <div class="sidebar-alert-card">
            <div class="sidebar-alert-header">
                Active Encroachment Violations
            </div>
            <div class="sidebar-alert-body">
                <strong>2 Synthetic Reference Cases</strong> | Total Encroached: <strong style="color:var(--danger);">9.60 m²</strong><br>
                <span>Adjacent Properties along East Road Corridor (Station 0+011.0 to 0+023.3)</span>
            </div>
        </div>

        <div style="font-size:11.5px; font-weight:700; color:var(--neutral-600); text-transform:uppercase; margin-bottom:8px; letter-spacing:0.4px;">
            Encroachment Cases (Field Verification Required):
        </div>

        <!-- Case E-01 Card -->
        <div class="sidebar-case-card" onclick="focusEncroachment('ENC-4A8C13E2')">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <strong style="color:var(--danger); font-size:13px;">Case E-01 (Top / North)</strong>
                <span class="badge badge-high">HIGH</span>
            </div>
            <div style="font-size:12px; line-height:1.5;">
                <strong>Property:</strong> H.No. 12-1-4, P-07 (Shanti Heights)<br>
                <strong>Structure:</strong> Awning / Canopy Extension<br>
                <strong>Encroached Area:</strong> <strong style="color:var(--danger); font-size:13px;">6.00 m²</strong><br>
                <strong>Projection:</strong> 1.20 m into ROW | <strong>Frontage:</strong> 5.00 m<br>
                <strong>Chainage:</strong> 0+011.0 | <span class="badge badge-ref">Synthetic Benchmark</span>
            </div>
            <div style="display:flex; gap:6px; margin-top:8px;">
                <button class="btn btn-secondary btn-sm" style="flex:1;" onclick="event.stopPropagation(); focusEncroachment('ENC-4A8C13E2')">Focus on Map</button>
                <button class="btn btn-primary btn-sm" style="flex:1;" onclick="event.stopPropagation(); openCaseModal('ENC-4A8C13E2')">Inspect</button>
            </div>
        </div>

        <!-- Case E-02 Card -->
        <div class="sidebar-case-card" onclick="focusEncroachment('ENC-FFF7E662')">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <strong style="color:var(--danger); font-size:13px;">Case E-02 (Bottom / South)</strong>
                <span class="badge badge-moderate">MODERATE</span>
            </div>
            <div style="font-size:12px; line-height:1.5;">
                <strong>Property:</strong> H.No. 12-1-6, P-08 (Surya Electricals)<br>
                <strong>Structure:</strong> Shop Extension / Veranda Shed<br>
                <strong>Encroached Area:</strong> <strong style="color:var(--danger); font-size:13px;">3.60 m²</strong><br>
                <strong>Projection:</strong> 0.80 m into ROW | <strong>Frontage:</strong> 4.50 m<br>
                <strong>Chainage:</strong> 0+023.3 | <span class="badge badge-ref">Synthetic Benchmark</span>
            </div>
            <div style="display:flex; gap:6px; margin-top:8px;">
                <button class="btn btn-secondary btn-sm" style="flex:1;" onclick="event.stopPropagation(); focusEncroachment('ENC-FFF7E662')">Focus on Map</button>
                <button class="btn btn-primary btn-sm" style="flex:1;" onclick="event.stopPropagation(); openCaseModal('ENC-FFF7E662')">Inspect</button>
            </div>
        </div>

        <div style="background:var(--neutral-50); border:1px solid var(--border); border-radius:var(--radius-sm); padding:10px 12px; margin-top:10px; font-size:11.5px; color:var(--text-secondary); line-height:1.45;">
            <strong style="color:var(--neutral-900);">Model Layer Separation:</strong><br>
            Trained baseline detects physical objects (<code>building</code>, <code>ramp</code>, <code>compound_wall</code>). Small structures (awning, veranda) utilize verified reference benchmark geometry. Toggle layers in the manager below.
        </div>
    `;
}

// Display Single YOLO Detection Detail
function showYoloDetail(props) {
    const detailBox = document.getElementById("sidebar-detail");
    const resetBtn = document.getElementById("btn-reset-sidebar");
    if (resetBtn) resetBtn.style.display = "inline-block";
    if (!detailBox) return;

    const isRoadFootpath = props.corridor_zone === 'BETWEEN_PAVED_ROAD_AND_FOOTPATH' || props.corridor_zone === 'FOOTPATH' || props.corridor_zone === 'PAVED_ROAD';

    detailBox.innerHTML = `
        <div style="background-color: var(--primary-light); border: 1px solid var(--primary-border); color: var(--primary); padding: 10px 12px; border-radius: 4px; font-weight: 600; margin-bottom: 12px; font-size:12px;">
            YOLO PHYSICAL STRUCTURE DETECTION<br>
            CONFIDENCE: ${(props.confidence * 100).toFixed(1)}%
        </div>

        <div style="margin-bottom:12px; font-size:12.5px; line-height:1.6;">
            <p><strong>Detection ID:</strong> <code>${props.detection_id}</code></p>
            <p><strong>Predicted Class:</strong> <strong>${props.class_name}</strong> (Class ID: ${props.class_id})</p>
            <p><strong>Corridor Zone:</strong> <span class="badge ${isRoadFootpath ? 'badge-critical' : 'badge-permissible'}">${props.corridor_zone || 'PRIVATE_PROPERTY'}</span></p>
            <p><strong>Zone Description:</strong> ${props.corridor_zone_desc || ''}</p>
            <p><strong>Encroachment Evaluation:</strong> ${
                isRoadFootpath
                ? '<strong style="color:var(--danger);">POTENTIAL ROAD ROW ENCROACHMENT (Field Verification Required)</strong>'
                : '<span style="color:#15803d; font-weight:600;">Permissible (Within Private Parcel)</span>'
            }</p>
            <p><strong>Model Architecture:</strong> ${props.model_architecture} (${props.model_weights || 'best.pt'})</p>
            <p><strong>Data Provenance:</strong> <span class="badge badge-yolo">${props.data_provenance}</span></p>
        </div>

        <div style="font-size:11.5px; color:var(--text-secondary); background:var(--neutral-50); border:1px solid var(--border); padding:8px 10px; border-radius:4px; margin-bottom:12px; line-height:1.45;">
            <strong>Road &amp; Footpath Compliance Rule:</strong><br>
            Any physical structure situated on or between the Paved Road (Carriageway) and Footpaths (Pedestrian Margins) is evaluated by the computational geometry engine as a potential encroachment.
        </div>

        <button class="btn btn-secondary btn-sm" onclick="renderDefaultSidebar()" style="width:100%;">← Back to All Cases</button>
    `;
}

// Display Single Benchmark Detail
function showBenchmarkDetail(props) {
    const detailBox = document.getElementById("sidebar-detail");
    const resetBtn = document.getElementById("btn-reset-sidebar");
    if (resetBtn) resetBtn.style.display = "inline-block";
    if (!detailBox) return;

    detailBox.innerHTML = `
        <div style="background-color: var(--danger-bg); border: 1px solid var(--danger-border); color: var(--danger); padding: 10px 12px; border-radius: 4px; font-weight: 600; margin-bottom: 12px; font-size:12px;">
            STATUS: ${props.status}<br>
            REQUIRED ACTION: ${props.action_required}
        </div>

        <div style="margin-bottom:12px; font-size:12.5px; line-height:1.6;">
            <p><strong>Case Reference:</strong> <code>${props.case_id}</code> (${props.benchmark_id || 'BENCHMARK'})</p>
            <p><strong>Encroached Zone:</strong> <span class="badge badge-high">${props.encroachment_zone || 'FOOTPATH'}</span></p>
            <p><strong>Corridor Location:</strong> ${props.corridor_position || 'Between Property Line & Paved Road'}</p>
            <p><strong>Property Parcel:</strong> <strong>${props.parcel_id}</strong></p>
            <p><strong>Structure Concept:</strong> ${props.structure_concept}</p>
            <p><strong>Spatial Justification:</strong> <small>${props.spatial_justification || ''}</small></p>
            <p><strong>Encroached Area:</strong> <span style="font-size:15px; font-weight:bold; color:var(--danger);">${props.area_sqm.toFixed(2)} m²</span></p>
            <p><strong>Max Projection Depth:</strong> <strong>${props.max_projection_m.toFixed(2)} m</strong> into footpath</p>
            <p><strong>Frontage Width:</strong> <strong>${props.frontage_m.toFixed(2)} m</strong> along corridor</p>
            <p><strong>Chainage Station:</strong> <code>${props.chainage_str}</code></p>
            <p><strong>Engineering Severity:</strong> <span class="badge badge-${props.severity.toLowerCase()}">${props.severity}</span></p>
            <p><strong>Data Provenance:</strong> <span class="badge badge-ref">${props.data_provenance}</span></p>
        </div>

        <div style="font-size:11.5px; color:var(--text-secondary); background:var(--neutral-50); border:1px solid var(--border); padding:8px 10px; border-radius:4px; margin-bottom:10px;">
            Academic reference benchmark geometry for geometric algorithm verification.
        </div>

        <button class="btn btn-primary btn-sm" onclick="openCaseModal('${props.case_id}')" style="width:100%; margin-bottom:6px;">Inspect Full Case Dossier</button>
        <button class="btn btn-secondary btn-sm" onclick="renderDefaultSidebar()" style="width:100%;">← Back to All Cases</button>
    `;
}

// Display Single Parcel Detail
function showParcelDetail(props) {
    const detailBox = document.getElementById("sidebar-detail");
    const resetBtn = document.getElementById("btn-reset-sidebar");
    if (resetBtn) resetBtn.style.display = "inline-block";
    if (!detailBox) return;

    const parts = (props.address_synthetic || "").split(",");
    const houseNo = props.house_no || (parts[0] ? parts[0].trim() : props.parcel_id);
    const plotNo = props.plot_no || (parts[1] ? parts[1].trim() : "");
    const cleanOwner = (props.owner_name_synthetic || "").replace(" (Synthetic)", "").trim();
    const hasCase = (props.parcel_id === 'P-07' || props.parcel_id === 'P-08');

    detailBox.innerHTML = `
        <div class="sidebar-title">Property Parcel: ${props.parcel_id}</div>
        <p style="margin-bottom:6px;"><strong>House Number:</strong> <span style="font-size:13.5px; font-weight:700; color:var(--primary);">${houseNo}</span> (${plotNo || props.parcel_id})</p>
        <p style="margin-bottom:6px;"><strong>Owner / Commercial Name:</strong> <strong>${cleanOwner}</strong></p>
        <p style="margin-bottom:6px;"><strong>Municipal Address:</strong> ${props.address_synthetic}</p>
        <p style="margin-bottom:6px;"><strong>Legal Parcel Area:</strong> ${props.area_sqm} m²</p>
        <p style="margin-bottom:12px;"><strong>Encroachment Status:</strong> ${
            hasCase
            ? '<span class="badge badge-high">Potential Encroachment Identified (Field Verification Required)</span>'
            : '<span class="badge badge-permissible">Permissible (Within Private Setback)</span>'
        }</p>
        <button class="btn btn-secondary btn-sm" onclick="renderDefaultSidebar()" style="width:100%;">← Back to Overview</button>
    `;
}

// Switch Map Display Modes
function setMapMode(mode) {
    const droneWrapper = document.getElementById("leaflet-map-wrapper");
    const vectorWrapper = document.getElementById("vector-map-wrapper");
    const layout = document.getElementById("map-layout-container");
    const btnDrone = document.getElementById("btn-mode-drone");
    const btnVec = document.getElementById("btn-mode-vector");
    const btnSplit = document.getElementById("btn-mode-split");

    [btnDrone, btnVec, btnSplit].forEach(b => { if (b) b.classList.remove("active"); });

    if (mode === "drone") {
        if (btnDrone) btnDrone.classList.add("active");
        if (droneWrapper) droneWrapper.style.display = "block";
        if (vectorWrapper) vectorWrapper.style.display = "none";
        if (layout) layout.className = "map-layout";
        if (map) setTimeout(() => map.invalidateSize(), 150);
    } else if (mode === "vector") {
        if (btnVec) btnVec.classList.add("active");
        if (droneWrapper) droneWrapper.style.display = "none";
        if (vectorWrapper) vectorWrapper.style.display = "block";
        if (layout) layout.className = "map-layout";
        if (vectorMap) setTimeout(() => vectorMap.invalidateSize(), 150);
    } else if (mode === "split") {
        if (btnSplit) btnSplit.classList.add("active");
        if (droneWrapper) droneWrapper.style.display = "block";
        if (vectorWrapper) vectorWrapper.style.display = "block";
        if (layout) layout.className = "split-map-layout";
        if (map) setTimeout(() => map.invalidateSize(), 150);
        if (vectorMap) setTimeout(() => vectorMap.invalidateSize(), 150);
    }
}

// Focus Specific Case on Map
function focusEncroachment(caseId) {
    const isVectorMode = document.getElementById("btn-mode-vector") && document.getElementById("btn-mode-vector").classList.contains("active");
    if (isVectorMode && vectorMap && window.vectorEncroachmentPolygons && window.vectorEncroachmentPolygons[caseId]) {
        const vLayer = window.vectorEncroachmentPolygons[caseId];
        vectorMap.fitBounds(vLayer.getBounds(), { maxZoom: 1, padding: [80, 80] });
        if (vLayer.openPopup) vLayer.openPopup();
        const feat = vLayer.feature;
        if (feat && feat.properties) {
            showBenchmarkDetail(feat.properties);
        }
        return;
    }
    const layer = window.encroachmentPolygons[caseId];
    if (layer && map) {
        setMapMode('drone');
        map.fitBounds(layer.getBounds(), { maxZoom: 2, padding: [60, 60] });
        layer.openPopup();
        const feat = layer.feature;
        if (feat && feat.properties) {
            showBenchmarkDetail(feat.properties);
        }
    }
}

// Reset Map Extent
function resetMapView() {
    if (map) {
        map.fitBounds([[0, 0], [723, 1024]]);
    }
    if (vectorMap) {
        vectorMap.fitBounds([[-5, -5], [40, 55]]);
    }
    renderDefaultSidebar();
}

// Prediction Viewer Gallery
function loadPredictionsGallery() {
    const gallery = document.getElementById("predictions-gallery");
    if (!gallery) return;

    const samplePreds = [
        { frame: "DRONE_SURVEY_R001_CORRIDOR", file: "/dataset/gis_outputs/encroachment_drone_overlay.jpg", classes: "E-01: Awning / Canopy (P-07) & E-02: Shop Extension Shed (P-08)" },
        { frame: "R001_SEQ03_FRAME001", file: "/runs/segmentation/predictions/R001_SEQ03_FRAME001_pred.jpg", classes: "building, compound_wall" },
        { frame: "R001_SEQ03_FRAME005", file: "/runs/segmentation/predictions/R001_SEQ03_FRAME005_pred.jpg", classes: "building, ramp" },
        { frame: "R001_SEQ03_FRAME015", file: "/runs/segmentation/predictions/R001_SEQ03_FRAME015_pred.jpg", classes: "building, ramp, compound_wall" },
    ];

    gallery.innerHTML = samplePreds.map(p => `
        <div class="gallery-card">
            <img src="${p.file}" alt="${p.frame}" onerror="this.src='https://via.placeholder.com/400x200?text=Prediction+Render+Unavailable'">
            <div class="gallery-card-body">
                <strong>Frame: ${p.frame}</strong>
                <p style="color:var(--text-secondary); font-size:11.5px; margin-top:4px;">Predicted Classes: ${p.classes}</p>
            </div>
        </div>
    `).join("");
}
