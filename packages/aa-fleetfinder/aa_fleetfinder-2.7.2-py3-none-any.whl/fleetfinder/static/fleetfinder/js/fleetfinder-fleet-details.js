/* global objectDeepMerge, aaFleetFinderSettings, aaFleetFinderSettingsOverride, fetchGet, fetchPost, fleetfinderBootstrapTooltip */

$(document).ready(() => {
    'use strict';

    const fleetFinderSettings = objectDeepMerge(aaFleetFinderSettings, aaFleetFinderSettingsOverride);

    /* DataTables
    ------------------------------------------------------------------------- */
    const elements = {
        tableFleetMembers: $('#table-fleet-members'),
        tableFleetComposition: $('#table-fleet-composition'),
        kickFleetMemberModal: $('#kick-fleet-member'),
        kickFleetMemberCharacterName: $('#kick-fleet-member-character-name'),
        modalButtonConfirmKickFleetMember: $('#modal-button-confirm-kick-fleet-member'),
        warning: $('#fleetfinder-fleet-details-warning')
    };
    const dataTableConfig = {
        language: {
            url: fleetFinderSettings.dataTables.languageUrl
        },
        paging: false,
        destroy: true
    };

    const populateDatatables = () => {
        fetchGet({
            url: fleetFinderSettings.dataTables.url.fleetDetails,
        })
            .then((data) => {
                if (data.error) {
                    elements.warning.removeClass('d-none').text(data.error);

                    return;
                }

                elements.warning.addClass('d-none');

                elements.tableFleetMembers.DataTable({
                    ...dataTableConfig,
                    data: data.fleet_member,
                    columns: [
                        {
                            render: (data, type, row) => {
                                const fwIcon = '<i class="fa-solid fa-star"></i>';

                                return row.is_fleet_boss ? `${row.character_name} <sup data-bs-tooltip="aa-fleetfinder" title="${fleetFinderSettings.l10n.fleetBoss}"><small>${fwIcon}</small></sup>` : row.character_name;
                            }
                        },
                        {data: 'ship_type_name'},
                        {data: 'solar_system_name'},
                        {
                            render: (data, type, row) => {
                                const fwIcon = '<i class="fa-solid fa-user-minus"></i>';
                                const dataAttributes = Object.entries({
                                    'data-character-id': row.character_id,
                                    'data-character-name': row.character_name,
                                    'data-bs-toggle': 'modal',
                                    'data-bs-target': '#kick-fleet-member',
                                    'data-bs-tooltip': 'aa-fleetfinder'
                                }).map(([key, value]) => {
                                    return `${key}="${value}"`;
                                }).join(' ');

                                return row.is_fleet_boss ? '' : `<button type="button" class="btn btn-sm btn-danger" ${dataAttributes} title="${fleetFinderSettings.l10n.kickMemberFromFleet}">${fwIcon}</button>`;
                            },
                            orderable: false,
                            searchable: false,
                            width: '50px',
                            className: 'text-end'
                        }
                    ],
                    createdRow: (row, data, rowIndex) => {
                        $(row).attr('data-row-id', rowIndex);
                        $(row).attr('data-character-id', data.character_id);
                    },
                    initComplete: () => {
                        // Initialize Bootstrap tooltips
                        fleetfinderBootstrapTooltip({selector: '#table-fleet-members'});
                    }
                });

                elements.tableFleetComposition.DataTable({
                    ...dataTableConfig,
                    data: data.fleet_composition,
                    columns: [
                        {data: 'ship_type_name'},
                        {data: 'number', className: 'text-right', width: '100px'}
                    ],
                    order: [[1, 'desc']]
                });
            })
            .catch((error) => {
                console.error('Error fetching fleet details:', error);
            });
    };

    populateDatatables();

    setInterval(populateDatatables, 30000);

    /* Modals
    ------------------------------------------------------------------------- */
    // Handle the kick fleet member modal
    elements.kickFleetMemberModal
        .on('show.bs.modal', (event) => {
            const button = $(event.relatedTarget);
            const characterId = button.data('character-id');
            const characterName = button.data('character-name');
            const link = fleetFinderSettings.dataTables.url.kickFleetMember;

            // Populate the modal content
            $('#kick-fleet-member-character-name').text(characterName);

            $('#modal-button-confirm-kick-fleet-member')
                // Remove any previous click handlers to avoid multiple bindings
                .off('click.kickMember')
                // Bind the click event for the confirmation button
                .on('click.kickMember', () => {
                    fetchPost({
                        url: link,
                        csrfToken: fleetFinderSettings.csrfToken,
                        payload: {
                            memberId: characterId
                        },
                        responseIsJson: true
                    })
                        .then(() => {
                            populateDatatables();

                            $('#kick-fleet-member').modal('hide');
                        })
                        .catch((error) => {
                            console.error('Error kicking fleet member:', error);

                            $('#kick-fleet-member .modal-kick-fleet-member-error')
                                .removeClass('d-none')
                                .find('.modal-kick-fleet-member-error-message')
                                .text(error || fleetFinderSettings.l10n.unknownError);
                        });
                });
        })
        .on('hide.bs.modal', () => {
            // Reset modal content
            $('#kick-fleet-member-character-name').empty();
            $('#kick-fleet-member .modal-kick-fleet-member-error')
                .addClass('d-none')
                .find('.modal-kick-fleet-member-error-message')
                .empty();

            // Clean up event handler
            $('#modal-button-confirm-kick-fleet-member').off('click.kickMember');
        });
});
