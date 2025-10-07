console.log('LogForge JavaScript file loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('LogForge Dashboard loaded');
    
    if (window.location.pathname.includes('/logs')) {
        console.log('Loading logs...');
        loadLogs();

        const userInput = document.getElementById('logs-search-user');
        const resourceTypeInput = document.getElementById('logs-search-resource-type');
        const batchInput = document.getElementById('logs-search-batch');
        const dataInput = document.getElementById('logs-search-data');
        const dateInput = document.getElementById('logs-search-date');

        const bind = (el, setter) => {
            if (!el) return;
            const debounced = debounce(() => { setter(el.value.trim()); loadLogs(1); }, 300);
            el.addEventListener('input', debounced);
        };

        bind(userInput, v => currentUserId = v);
        bind(resourceTypeInput, v => currentResourceType = v);
        bind(batchInput, v => currentBatchUuid = v);
        bind(dataInput, v => currentDataQuery = v);
        bind(dateInput, v => currentDate = v);

        document.addEventListener('click', function(e) {
            const row = e.target.closest('tr[data-log-id]');
            if (row && !e.target.closest('button')) {
                const logId = row.getAttribute('data-log-id');
                if (logId) {
                    handleRowClick(logId);
                }
            }
        });
    }

    if (window.location.pathname === '/logforge' || window.location.pathname === '/logforge/') {
        loadEventTypeStats();
        loadResourceTypeStats();
        loadTopUsersStats();
    }
});

let currentPage = 1;
let currentUserId = '';
let currentResourceType = '';
let currentBatchUuid = '';
let currentDataQuery = '';
let currentDate = '';

async function loadLogs(page = 1) {
    try {
        const params = new URLSearchParams();
        params.set('page', String(page));
        if (currentUserId) params.set('user_id', currentUserId);
        if (currentResourceType) params.set('resource_type', currentResourceType);
        if (currentBatchUuid) params.set('batch_uuid', currentBatchUuid);
        if (currentDataQuery) params.set('data_q', currentDataQuery);
        if (currentDate) params.set('date', currentDate);
        const response = await fetch(`/logforge/api/logs?${params.toString()}`);
        const data = await response.json();
        
        renderLogsTable(data.logs);
        renderPagination(data.pagination);
        currentPage = page;
    } catch (error) {
        console.error('Failed to load logs:', error);
        const tbody = document.getElementById('logs-table-body');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="9" class="px-4 py-4 text-center text-gray-500">Failed to load logs</td></tr>';
        }
    }
}

function renderLogsTable(logs) {
    console.log('renderLogsTable called with:', logs);
    const tbody = document.getElementById('logs-table-body');
    
    if (!tbody) {
        console.error('logs-table-body element not found!');
        return;
    }
    
    if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="px-4 py-4 text-center text-gray-500">No logs found</td></tr>';
        return;
    }
    
    const rows = logs.map(log => `
        <tr class="hover:bg-gray-50 transition-colors duration-150 cursor-pointer" data-log-id="${log.id}" title="View details">
            <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900 text-center"><span class="truncate-mono" style="max-width:160px; display:inline-block;">${log.id}</span></td>
            <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900 text-center">${formatDate(log.created_at)}</td>
            <td class="px-4 py-4 whitespace-nowrap text-center">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getEventBadgeClass(log.event_type)}">
                    ${log.event_type}
                </span>
            </td>
            <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500 text-center"><span class="truncate-mono" style="max-width:140px; display:inline-block;">${log.user_id || '—'}</span></td>
            <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900 text-center">
                <div class="font-medium truncate" style="max-width:180px; margin:0 auto;">${log.resource_type}</div>
                <div class="text-gray-500 text-xs truncate-mono" style="max-width:180px; margin:0 auto;">#${log.resource_id}</div>
            </td>
            <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500 text-center"><span class="truncate-mono" style="max-width:180px; display:inline-block;">${log.batch_uuid || '—'}</span></td>
            <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500 text-center"><span class="truncate" style="max-width:120px; display:inline-block;">${log.ip_address || '—'}</span></td>
            <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500 text-center"><span class="truncate-mono" style="max-width:220px; display:inline-block;">${log.context ? JSON.stringify(log.context) : '—'}</span></td>
            <td class="px-4 py-4 whitespace-nowrap text-sm text-center">
                <a href="/logforge/logs/${log.id}" onclick="event.stopPropagation();" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium transition-colors inline-block">
                    View
                </a>
            </td>
        </tr>
    `).join('');
    
    tbody.innerHTML = rows;

    if (!tbody.dataset.clickBound) {
        tbody.addEventListener('click', function(e) {
            if (e.target && e.target.closest('button')) {
                return;
            }
            const row = e.target.closest('tr[data-log-id]');
            if (row) {
                const id = row.getAttribute('data-log-id');
                if (id) {
                    handleRowClick(id);
                }
            }
        });
        tbody.dataset.clickBound = '1';
    }
}

function renderPagination(pagination) {
    const info = document.getElementById('pagination-info');
    const controls = document.getElementById('pagination-controls');
    
    const start = (pagination.current_page - 1) * pagination.per_page + 1;
    const end = Math.min(pagination.current_page * pagination.per_page, pagination.total_items);
    info.textContent = `Showing ${start}-${end} of ${pagination.total_items} entries`;
    
    const prevBtn = `<button onclick="loadLogs(${pagination.current_page - 1})" class="btn" ${!pagination.has_prev ? 'disabled' : ''}>Previous</button>`;
    const nextBtn = `<button onclick="loadLogs(${pagination.current_page + 1})" class="btn" ${!pagination.has_next ? 'disabled' : ''}>Next</button>`;
    controls.innerHTML = prevBtn + nextBtn;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function handleRowClick(logId) {
    try {
        window.location.href = `/logforge/logs/${logId}`;
    } catch (error) {
        console.error('Navigation error:', error);
    }
}

window.handleRowClick = handleRowClick;

function getEventBadgeClass(eventType) {
    switch(eventType) {
        case 'create': return 'bg-green-100 text-green-800';
        case 'update': return 'bg-yellow-100 text-yellow-800';
        case 'delete': return 'bg-red-100 text-red-800';
        case 'restore': return 'bg-blue-100 text-blue-800';
        case 'force_delete': return 'bg-red-100 text-red-800';
        case 'bulk_operation': return 'bg-purple-100 text-purple-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

function debounce(fn, wait) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), wait);
    };
}

async function loadEventTypeStats() {
    try {
        const res = await fetch('/logforge/api/stats/event-types');
        const payload = await res.json();
        const rows = payload.data || [];
        renderPieChart(rows);
        renderLegend(rows);
    } catch (e) {
        console.error('Failed to load stats', e);
    }
}

function renderPieChart(rows) {
    const svg = document.getElementById('lf-pie');
    if (!svg) return;
    const total = rows.reduce((s, r) => s + Number(r.count || 0), 0) || 1;
    const box = svg.viewBox.baseVal;
    const cx = (box && box.width) ? box.width / 2 : 180;
    const cy = (box && box.height) ? box.height / 2 : 180;
    const r = Math.min(cx, cy) - 40;
    let angle = 0;
    svg.innerHTML = '';
    const colors = ['#10b981','#f59e0b','#ef4444','#3b82f6','#8b5cf6','#14b8a6','#f97316','#22c55e'];
    const eventOrder = { create: 1, update: 2, delete: 3, restore: 4, force_delete: 5, bulk_operation: 6 };
    const paths = [];
    const labels = [];
    rows.forEach((row, i) => {
        const value = Number(row.count || 0);
        const portion = value / total;
        const theta = portion * Math.PI * 2;
        const x1 = cx + r * Math.cos(angle);
        const y1 = cy + r * Math.sin(angle);
        const x2 = cx + r * Math.cos(angle + theta);
        const y2 = cy + r * Math.sin(angle + theta);
        const largeArc = theta > Math.PI ? 1 : 0;
        const d = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', d);
        path.setAttribute('fill', colors[i % colors.length]);
        path.setAttribute('opacity', '0.9');
        svg.appendChild(path);
        paths.push({ path, start: angle, end: angle + theta, largeArc });

        const mid = angle + theta / 2;
        const labelInsideRadius = r * 0.6;
        const labelOutsideRadius = r + 16;
        const label = String(row.event_type || '');
        const ordinal = eventOrder[label] ?? (i + 1);

        if (portion >= 0.04) {
            const lx = cx + labelInsideRadius * Math.cos(mid);
            const ly = cy + labelInsideRadius * Math.sin(mid);
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', String(lx));
            text.setAttribute('y', String(ly));
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dominant-baseline', 'middle');
            text.setAttribute('fill', '#ffffff');
            text.setAttribute('font-size', '12');
            text.setAttribute('font-weight', '600');
            text.textContent = String(ordinal);
            text.setAttribute('opacity', '0');
            svg.appendChild(text);
            labels.push(text);
        } else if (portion > 0) {
            const xEdge = cx + r * Math.cos(mid);
            const yEdge = cy + r * Math.sin(mid);
            const lx = cx + labelOutsideRadius * Math.cos(mid);
            const ly = cy + labelOutsideRadius * Math.sin(mid);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', String(xEdge));
            line.setAttribute('y1', String(yEdge));
            line.setAttribute('x2', String(lx));
            line.setAttribute('y2', String(ly));
            line.setAttribute('stroke', '#9ca3af');
            line.setAttribute('stroke-width', '1');
            svg.appendChild(line);

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', String(lx));
            text.setAttribute('y', String(ly));
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dominant-baseline', 'middle');
            text.setAttribute('fill', '#374151');
            text.setAttribute('font-size', '12');
            text.setAttribute('font-weight', '600');
            text.textContent = String(ordinal);
            text.setAttribute('opacity', '0');
            svg.appendChild(text);
            labels.push(text);
        }
        angle += theta;
    });

    const startTs = performance.now();
    const duration = 800;
    function drawFrame(ts) {
        const t = Math.min(1, (ts - startTs) / duration);
        const eased = 1 - Math.pow(1 - t, 3);
        paths.forEach(seg => {
            const currentAngle = seg.start + (seg.end - seg.start) * eased;
            const x1 = cx + r * Math.cos(seg.start);
            const y1 = cy + r * Math.sin(seg.start);
            const x2 = cx + r * Math.cos(currentAngle);
            const y2 = cy + r * Math.sin(currentAngle);
            const largeArc = (currentAngle - seg.start) > Math.PI ? 1 : 0;
            const d = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;
            seg.path.setAttribute('d', d);
        });
        labels.forEach(el => el.setAttribute('opacity', String(eased)));
        if (t < 1) requestAnimationFrame(drawFrame);
    }
    requestAnimationFrame(drawFrame);
}

function renderLegend(rows) {
    const el = document.getElementById('lf-legend');
    if (!el) return;
    const colors = ['#10b981','#f59e0b','#ef4444','#3b82f6','#8b5cf6','#14b8a6','#f97316','#22c55e'];
    const eventOrder = { create: 1, update: 2, delete: 3, restore: 4, force_delete: 5, bulk_operation: 6 };
    const sorted = [...rows].sort((a, b) => {
        const na = eventOrder[String(a.event_type || 'unknown')] ?? 999;
        const nb = eventOrder[String(b.event_type || 'unknown')] ?? 999;
        return na - nb;
    });
    el.innerHTML = sorted.map((r, i) => {
        const color = colors[i % colors.length];
        const label = String(r.event_type || 'unknown');
        const num = eventOrder[label] ?? (i + 1);
        return `<div class="flex items-center">
            <span class="inline-block w-4 h-4 rounded-sm mr-2" style="background:${color}"></span>
            <span class="text-gray-700">${num}. ${escapeHtml(label)}</span>
        </div>`;
    }).join('');
}

function escapeHtml(str) {
    return String(str).replace(/[&<>\"]+/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
}

async function loadResourceTypeStats() {
    try {
        const res = await fetch('/logforge/api/stats/resource-types');
        const payload = await res.json();
        renderBarChart('lf-bar-resource', payload.data || [], 'resource_type');
    } catch (e) { console.error('resource types stats failed', e); }
}

async function loadTopUsersStats() {
    try {
        const res = await fetch('/logforge/api/stats/top-users');
        const payload = await res.json();
        renderBarChart('lf-bar-users', payload.data || [], 'user_id');
    } catch (e) { console.error('top users stats failed', e); }
}

function renderBarChart(svgId, rows, labelKey) {
    const svg = document.getElementById(svgId);
    if (!svg) return;
    const width = 640, height = 260;
    const padding = { left: 60, bottom: 30, right: 10, top: 10 };
    const innerWidth = width - padding.left - padding.right;
    const innerHeight = height - padding.top - padding.bottom;
    const max = Math.max(1, ...rows.map(r => Number(r.count || 0)));
    const autoBarWidth = innerWidth / Math.max(1, rows.length);
    const singleBar = rows.length === 1;
    const barWidth = singleBar ? Math.min(80, innerWidth / 3) : autoBarWidth;
    svg.innerHTML = '';

    const ax = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    ax.setAttribute('x1', String(padding.left));
    ax.setAttribute('y1', String(height - padding.bottom));
    ax.setAttribute('x2', String(width - padding.right));
    ax.setAttribute('y2', String(height - padding.bottom));
    ax.setAttribute('stroke', '#e5e7eb');
    svg.appendChild(ax);

    const bars = [];
    const labels = [];
    const valueLabels = [];
    rows.forEach((r, i) => {
        const val = Number(r.count || 0);
        const h = (val / max) * (innerHeight - 10);
        const startOffset = singleBar ? (innerWidth - barWidth) / 2 : 0;
        const x = padding.left + startOffset + i * barWidth + 8;
        const y = height - padding.bottom - h;
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', String(x));
        rect.setAttribute('y', String(height - padding.bottom));
        rect.setAttribute('width', String(Math.max(10, barWidth - 16)));
        rect.setAttribute('height', '0');
        rect.setAttribute('fill', '#3b82f6');
        rect.setAttribute('opacity', '0.85');
        svg.appendChild(rect);
        bars.push({ rect, y, h });

        const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        txt.setAttribute('x', String(x + Math.max(10, barWidth - 16) / 2));
        txt.setAttribute('y', String(height - padding.bottom + 16));
        txt.setAttribute('text-anchor', 'middle');
        txt.setAttribute('fill', '#6b7280');
        txt.setAttribute('font-size', '10');
        txt.textContent = String(r[labelKey] ?? '—');
        svg.appendChild(txt);
        labels.push(txt);

        const vtxt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        vtxt.setAttribute('x', String(x + Math.max(10, barWidth - 16) / 2));
        vtxt.setAttribute('y', String(height - padding.bottom - 4));
        vtxt.setAttribute('text-anchor', 'middle');
        vtxt.setAttribute('fill', '#374151');
        vtxt.setAttribute('font-size', '10');
        vtxt.textContent = String(val);
        vtxt.setAttribute('opacity', '0');
        svg.appendChild(vtxt);
        valueLabels.push({ el: vtxt, y });
    });

    const startTs = performance.now();
    const duration = 700;
    function grow(ts) {
        const t = Math.min(1, (ts - startTs) / duration);
        const eased = 1 - Math.pow(1 - t, 3);
        bars.forEach(b => {
            const ch = b.h * eased;
            const cy = b.y + (b.h - ch);
            b.rect.setAttribute('height', String(ch));
            b.rect.setAttribute('y', String(cy));
        });
        valueLabels.forEach(v => v.el.setAttribute('opacity', String(eased)));
        if (t < 1) requestAnimationFrame(grow);
    }
    requestAnimationFrame(grow);
}

// Placeholder; to be replaced with Laravel JS content for exact parity

