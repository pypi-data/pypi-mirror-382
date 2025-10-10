// Luxin Interactive Table JavaScript

(function() {
    // Store the source mapping and detail data
    const sourceMapping = {source_mapping};
    const detailData = {detail_data};
    const groupbyCols = {groupby_cols};
    
    // Use unique ID to target this specific instance
    const uniqueId = '{unique_id}';
    
    // Get DOM elements
    const detailPanel = document.getElementById('detail-panel-' + uniqueId);
    const detailContent = document.getElementById('detail-content-' + uniqueId);
    const closeButton = document.getElementById('close-panel-' + uniqueId);
    const mainTable = document.getElementById('main-table-' + uniqueId);
    
    if (!detailPanel || !detailContent || !closeButton || !mainTable) {
        console.error('Luxin: Could not find required DOM elements for instance', uniqueId);
        return;
    }
    
    // Get all data rows (skip header)
    const dataRows = mainTable.querySelectorAll('tbody tr');
    
    // Add click handlers to rows
    dataRows.forEach((row, index) => {
        row.addEventListener('click', function() {
            // Remove selected class from all rows
            dataRows.forEach(r => r.classList.remove('selected'));
            
            // Add selected class to clicked row
            this.classList.add('selected');
            
            // Get the row key based on index values
            const rowKey = getRowKey(index);
            
            // Show detail panel with data
            showDetailPanel(rowKey);
        });
    });
    
    // Close button handler
    closeButton.addEventListener('click', function() {
        closeDetailPanel();
    });
    
    // Close panel when clicking outside
    document.addEventListener('click', function(event) {
        if (detailPanel.classList.contains('open') && 
            !detailPanel.contains(event.target) && 
            !mainTable.contains(event.target)) {
            closeDetailPanel();
        }
    });
    
    function getRowKey(rowIndex) {
        // Get the row key from the data
        const keys = Object.keys(sourceMapping);
        if (rowIndex < keys.length) {
            return keys[rowIndex];
        }
        return null;
    }
    
    function showDetailPanel(rowKey) {
        if (!rowKey || !sourceMapping[rowKey]) {
            detailContent.innerHTML = '<p class="detail-placeholder">No detail data available for this row</p>';
            detailPanel.classList.add('open');
            return;
        }
        
        // Get the indices of detail rows
        const detailIndices = sourceMapping[rowKey];
        
        // Build the detail table
        const detailHtml = buildDetailTable(detailIndices);
        detailContent.innerHTML = detailHtml;
        
        // Open the panel
        detailPanel.classList.add('open');
    }
    
    function buildDetailTable(indices) {
        if (!indices || indices.length === 0) {
            return '<p class="detail-placeholder">No detail rows found</p>';
        }
        
        // Get the detail rows
        const rows = indices.map(idx => detailData[idx]).filter(row => row !== undefined);
        
        if (rows.length === 0) {
            return '<p class="detail-placeholder">No detail rows found</p>';
        }
        
        // Get column names from first row
        const columns = Object.keys(rows[0]);
        
        // Build HTML table
        let html = '<table><thead><tr>';
        columns.forEach(col => {
            html += `<th>${escapeHtml(col)}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        rows.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                const value = row[col];
                html += `<td>${escapeHtml(String(value))}</td>`;
            });
            html += '</tr>';
        });
        
        html += '</tbody></table>';
        html += `<p style="margin-top: 15px; color: #666; font-size: 13px;">Showing ${rows.length} detail row${rows.length !== 1 ? 's' : ''}</p>`;
        
        return html;
    }
    
    function closeDetailPanel() {
        detailPanel.classList.remove('open');
        dataRows.forEach(r => r.classList.remove('selected'));
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
})();

