/* global aaFleetFinderSettings, aaFleetFinderSettingsOverride, objectDeepMerge, fetchGet, fleetfinderBootstrapTooltip, DataTable */

$(document).ready(() => {
    'use strict';

    const fleetFinderSettings = objectDeepMerge(aaFleetFinderSettings, aaFleetFinderSettingsOverride);

    const table_fleet_overview = $('#table_available-fleets');
    let dataTable = null;

    /**
     * Initialize or update the datatable.
     * If the table already exists, it will be updated with new data.
     * If it does not exist, a new DataTable will be created.
     *
     * @param {Object} data - The fleet data to populate the table.
     */
    const initializeOrUpdateTable = (data) => {
        if (dataTable) {
            // Update existing table
            dataTable.clear().rows.add(data).draw();
        } else {
            // Initialize new table
            dataTable = table_fleet_overview.DataTable({
                language: {
                    url: fleetFinderSettings.dataTables.languageUrl
                },
                data: data,
                columns: [
                    {
                        data: 'fleet_commander',
                        render: {
                            _: 'html',
                            sort: 'sort'
                        }
                    },
                    {
                        data: 'fleet_name'
                    },
                    {
                        data: 'created_at',
                    },
                    {
                        data: 'actions',
                        className: 'text-end',
                    },
                ],
                columnDefs: [
                    {
                        targets: 2,
                        render: DataTable.render.date(
                            fleetFinderSettings.dataTables.datetimeFormat
                        )
                    },
                    {
                        orderable: false,
                        targets: [3]
                    },
                ],
                order: [[0, 'asc']],
                paging: false,
                initComplete: () => {
                    // Initialize Bootstrap tooltips
                    fleetfinderBootstrapTooltip({selector: '#table_available-fleets'});
                }
            });
        }
    };

    /**
     * Fetch and update fleet data
     */
    const fetchFleetData = () => {
        fetchGet({url: fleetFinderSettings.dataTables.url.dashboard})
            .then(initializeOrUpdateTable)
            .catch((error) => {
                console.error('Error fetching fleet data:', error);
            });
    };

    // Initial load
    fetchFleetData();

    // Refresh every 30 seconds
    setInterval(fetchFleetData, 30000);
});
