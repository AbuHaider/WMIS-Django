
// Declare Global Variable :: 
var csrftoken = $("meta[name='csrf-token']").attr("content");
var userName = $('#user_name').val();
var userType = $('#userType').val();

var map; 
var mapZoom = 7.25;
var mapCenter = [23.80466803926892, 90.583723353677];
var layers = {};



$(function () {

    console.log("Map View JS loaded..");

    map = new L.Map("map",
    {
        dragging: true,
        scrollWheelZoom: "center",
        zoomControl: false,
        zoomDelta: 0.25,
        zoomSnap: 0,
        maxZoom: 18,
        minZoom: 3,
        zoom: mapZoom,
        fadeAnimation: true,
        zoomAnimation: true
    })
    .setView(mapCenter, mapZoom);
    
    // Set the default layer
    openStreetLayer.addTo(map);
    // googleSatelliteLayer.addTo(map);

    fullExtendMap();
    getDivisionMap(); // BD Area Map
    getWatershedBoundaryMap(); // Initial Map
    mapLayers();
    initializeLegend();

    $(document).on('change', '.content-category', function() {
        
        var category_val = $(this).val();
        var action = $(this).is(':checked') ? 'add' : 'remove';

        var watershed_code = $('#watershed-select option:selected').val();
        if (!watershed_code && action === 'add') {
            alert("Please select a watershed first !");
            return;
        } else if (!watershed_code && action === 'remove') {
            return;
        }

        var category_id = watershed_code +'_'+ category_val;

        const geoCategories = new Set(['soil', 'slope', 'land_use', 'topography']);
        if (geoCategories.has(category_val)) {
            watershed_code = category_id;
        }

        console.log(category_id, ' : ', watershed_code);

        $.ajax({
            type: "POST",
            url: "/get-shape-file-path-and-map-legend-info/",
            headers: { "X-CSRFToken": csrftoken },
            data: { 'dataToSend' : category_id, 'p_watershed_id': watershed_code },
            dataType: "json",
            cache: false,
            success: function (data) {
                console.log(data);
                if (data.response.map_data.length > 0) {
                    var shape_file_path = data.response.map_data[0].file_path;
                    var layer_color = data.response.layer_color;
                    var legend_info = data.response.legend_data;
                    // console.log("File Path :", shape_file_path, "Color : ", legend_color);
                    $('.tabular-div-popup').fadeOut('slow');

                    if (action === 'add') {

                        // Remove previous fill color layer if exists
                        if (currentParaBoundaryLayer) {
                            map.removeLayer(currentParaBoundaryLayer);
                            currentParaBoundaryLayer = null;
                        }

                        const geoCategories = new Set(['soil', 'slope', 'land_use', 'topography']);
                        if (geoCategories.has(category_val)) {
                            getCategoryWiseNaturalMap(category_id, category_val, shape_file_path, layer_color, legend_info);
                        } 
                        
                        getCategoryWiseMap(category_id, category_val, shape_file_path, layer_color, legend_info);

                    } else {
                        // Remove the old one layer
                        if (storeCategoryWiseLayer) {
                            map.removeLayer(storeCategoryWiseLayer);
                        } 

                        // Clear previous labels before creating new ones
                        labelParaNames.forEach(label => map.removeLayer(label));
                        labelParaNames = [];

                        // Clear previous labels before creating new ones
                        storeParaLabel.forEach(label => map.removeLayer(label));
                        storeParaLabel = [];
            
                        $('#watershed-select').trigger('change');
                    }

                } else {
                    alert(data.message);
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                console.log(thrownError + "\r\n" + xhr.statusText + "\r\n" + xhr.responseText);
            }
        });    

    });

    $(document).on('change', '#district-select', function() {
        const district = $(this).val();
        if (!district) return;

        districtWiseCloseMap(district);

        if (watershedBoundaryLayer) {
            map.removeLayer(watershedBoundaryLayer);
        }

        // Remove previous fill color layer if exists
        if (currentWatershedFillLayer) {
            map.removeLayer(currentWatershedFillLayer);
            currentWatershedFillLayer = null;
        }

        districtWiseWatershedFillColor(district);
        
        const $watershedSelect = $('#watershed-select');
        
        $.ajax({
            url: '/get-district-wise-watershed-list/',
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: { district: district },
            success: function(response) {
                $watershedSelect.empty();
                
                if (response.status && response.watersheds?.length) {
                    $watershedSelect.append(
                        '<option value="" disabled selected class="text-gray-400">Select Watershed</option>'
                    );
                    
                    $.each(response.watersheds, function(index, watershed) {
                        $watershedSelect.append(
                            $('<option>', {
                                value: watershed.watershed_code,
                                class: 'text-gray-800',
                                text: watershed.watershed_name +' ('+ watershed.watershed_code + ')'
                            })
                        );
                    });
                    
                    $watershedSelect.prop('disabled', false);
                    $('.tabular-div-popup').fadeOut('slow');
                    $('.content-category').prop('checked', false);
                } else {
                    $watershedSelect.append(
                        '<option value="" disabled class="text-gray-400">No watersheds found</option>'
                    );
                }
            },
            error: function(xhr) {
                $watershedSelect.empty().append(
                    '<option value="" disabled class="text-gray-400">Error loading data</option>'
                );
                console.error('Error:', xhr.responseText);
            }
        });
    });

    $(document).on('change', '#watershed-select', function() {
        const watershed = $(this).val();
        if (!watershed) return;

        console.log('Watershed is : ', watershed);

        $.ajax({
            type: "POST",
            url: "/get-shape-file-path-and-para-legend-info/",
            headers: { "X-CSRFToken": csrftoken },
            data: { 'dataToSend' : watershed },
            dataType: "json",
            cache: false,
            success: function (data) {
                console.log(data);
                if (data.response.map_data.length > 0) {
                    var shape_file_path = data.response.map_data[0].file_path;
                    var legend_info = data.response.legend_data;
                    // console.log("File Path :", shape_file_path, "Color : ", legend_info);
                    
                    // Remove previous fill color layer if exists
                    if (divisionMapLayer) {
                        map.removeLayer(divisionMapLayer);
                    }

                    if (watershedBoundaryLayer) {
                        map.removeLayer(watershedBoundaryLayer);
                    }
            
                    if (currentWatershedFillLayer) {
                        map.removeLayer(currentWatershedFillLayer);
                        currentWatershedFillLayer = null;
                    }

                    // Clear previous labels
                    currentWatershedLabels.forEach(label => map.removeLayer(label));
                    currentWatershedLabels = [];

                    labelParaNames.forEach(label => map.removeLayer(label));
                    labelParaNames = [];

                    watershedWiseCloseMap(watershed);
                    getWatershedParaBoundaryMap(shape_file_path, legend_info);
                    // updateLegend(action, data.response.legend_data);
                    $('.tabular-div-popup').fadeOut('slow');
                    $('.content-category').prop('checked', false);

                } else {
                    alert(data.message);
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                console.log(thrownError + "\r\n" + xhr.statusText + "\r\n" + xhr.responseText);
            }
        });

    });

    $(document).on('click', '#contentLink', function(){
        $('#contentDiv').show();
        $('#legendDiv').hide();
        $('#watershedDiv').show();

        $('#contentLink').css({ 'color': 'white'});
        $('#legendLink').css({ 'color': 'black'});
    });

    $(document).on('click', '#legendLink', function(){
        $('#contentDiv').hide();
        $('#legendDiv').show();
        $('#watershedDiv').hide();

        $('#legendLink').css({ 'color': 'white'});
        $('#contentLink').css({ 'color': 'black'});

    });

    $(document).on('click', '#map_legend_hide', function(){
        $('.mapLegendCont').hide();
        $('.legend-icon').fadeIn('slow');
    });

    $(document).on('click', '#show_map_legend', function(){
        $('.legend-icon').hide();
        $('.mapLegendCont').fadeIn('slow');
    });

    $(document).on('click', '#mapLayer', function(){
        $('.dropdown-content').fadeIn('slow');
    });

    $('#close_tabular_popup_div').click(function (){
        $('.tabular-div-popup').fadeOut('slow');
    });

    $(window).on('click', function(event) {
        if (!$(event.target).closest('#mapLayer').length) {
            $('.dropdown-content').fadeOut('slow');
        }
    });

    $('#refresh_page').click(function() {
        location.reload(true);
    });

    $('.treeview input[type="checkbox"]').change(function () {
        // Get the parent <li> of the current checkbox
        const parentLi = $(this).closest('li');

        // Close all sibling <ul> elements at the same level
        parentLi.siblings().find('input[type="checkbox"]').prop('checked', false);

        // Close all other top-level <ul> elements outside the current hierarchy
        parentLi.parentsUntil('.treeview').siblings().find('input[type="checkbox"]').prop('checked', false);
    });

});


var divisionMapLayer;
function getDivisionMap () {
    var getFilePath = '/static/map_files/division.json';

    $.getJSON(getFilePath, function(data) {
        divisionMapLayer = L.geoJson(data, {
            style: function(feature) {
                return {
                    color: 'Black',
                    weight: 1,
                    opacity: 0.3,
                    fillColor: 'None',
                    // fillColor: v_fillColor,
                    fillOpacity: 0,
                };
            }
        }).addTo(map);
    });

}

var watershedBoundaryLayer;
function getWatershedBoundaryMap () {

    var getFilePath = '/static/map_files/cht_all_watershed.json';
    $.getJSON(getFilePath, function(geoJsonData) {

        const zilaColors = {
            'Bandarban': '#804A00',
            'Rangamati': 'Blue',
            'Khagrachhari': '#045D5D'
        };
        
        watershedBoundaryLayer = L.geoJson(geoJsonData, {
            style: function(feature) {
                return {
                    color: 'none',
                    weight: 0.7,
                    opacity: 0.6,
                    fillColor: zilaColors[feature.properties.ZILA] || 'none',
                    fillOpacity: 0.5,
                };
            }
        }).addTo(map);
    
        initializeLegend(zilaColors);
    
        map.on('zoomend', function() {
            watershedBoundaryLayer.eachLayer(function(layer) {
                updateWatershedLabel(layer, layer.feature);
            });
        });
    });

}

var currentWatershedFillLayer = null;
var currentWatershedLabels = [];
function districtWiseWatershedFillColor(district_name) {
    var getFilePath = '/static/map_files/cht_all_watershed.json';

    // Clear previous labels
    currentWatershedLabels.forEach(label => map.removeLayer(label));
    currentWatershedLabels = [];

    $.getJSON(getFilePath, function(geoJsonData) {

        const zilaColors = {
            'Bandarban': '#804A00',
            'Rangamati': 'Blue',
            'Khagrachhari': '#045D5D'
        };

        const districtAreas = {
            'Rangamati': ['R114', 'R65', 'R99'],
            'Bandarban': ['B76', 'B77', 'B173'],
            'Khagrachhari': ['K76', 'K98', 'K71']
        };
        
        var newLayer = L.geoJson(geoJsonData, {
            style: function(feature) {

                let style = {
                    color: 'none',
                    weight: 0.8,
                    opacity: 0.8,
                    fillColor: 'none',
                    fillOpacity: 0.6,
                };
                
                if (district_name && feature.properties.ZILA === district_name) {
                    style.fillColor = zilaColors[feature.properties.ZILA] || 'none';
                    // style.color = 'orange';
                    
                    if (districtAreas[district_name]) {
                        const areaCode = feature.properties.SL_NO;
                        if (districtAreas[district_name].includes(areaCode)) {
                            style.fillColor = 'red';
                        }
                    }
                }
                
                return style;
            },
            onEachFeature: function(feature, layer) {
                if (district_name && feature.properties.ZILA === district_name) {
                    const areaCode = feature.properties.SL_NO;
                    if (districtAreas[district_name] && districtAreas[district_name].includes(areaCode)) {
                        // Get the center of the polygon
                        const center = layer.getBounds().getCenter();
                        // Create a label at the center
                        const label = L.marker(center, {
                            icon: L.divIcon({
                                className: 'watershed-label',
                                html: areaCode,
                                iconSize: [30, 30]
                            }),
                            zIndexOffset: 1000
                        }).addTo(map);
                        currentWatershedLabels.push(label);
                    }
                }
            }
        }).addTo(map);

        // Store the new layer reference and remove the old one
        if (currentWatershedFillLayer) {
            map.removeLayer(currentWatershedFillLayer);
        }
        currentWatershedFillLayer = newLayer;
    
        getDistrictWiseWatershedLegend(districtAreas);
    
        // map.on('zoomend', function() {
        //     newLayer.eachLayer(function(layer) {
        //         updateWatershedLabel(layer, layer.feature);
        //     });
        // });
    });

}

var currentParaBoundaryLayer = null;
var labelParaNames = [];
function getWatershedParaBoundaryMap(shapeFile_path, paraColor_info) {

    $.getJSON(shapeFile_path, function(geoJsonData) {
        var newLayer = L.geoJson(geoJsonData, {
            style: function(feature) {
                let v_fillColor = 'orange';
                
                if (Array.isArray(paraColor_info) && feature.properties.Para_Name) {
                    // Find the matching para_name in paraColor_info array
                    const matchingItem = paraColor_info.find(item => 
                        item.para_name === feature.properties.Para_Name
                    );
                    
                    if (matchingItem && matchingItem.para_map_color) {
                        v_fillColor = matchingItem.para_map_color;
                    }
                }

                return {
                    color: 'black',
                    weight: '1',
                    opacity: 0.3,
                    fillColor: v_fillColor,
                    fillOpacity: 0,
                };
            },
            onEachFeature: function(feature, layer) {
                var name = feature.properties.Para_Name;
                var center = [feature.properties.YCoor, feature.properties.XCoor];

                // Add the label at the center position
                var label = L.marker(center, {
                    icon: L.divIcon({
                        className: 'label',
                        html: `<div style="font-family: 'Cambria';">${name}</div>`
                    })
                }).addTo(map);

                labelParaNames.push(label); // Track the label marker

                setTimeout(function() {
                    layer.setStyle({
                        fillOpacity: 0.8
                    });
                }, 50);

                layer.on('mouseover', function(event) {
                    layer.getElement().style.cursor = 'default';
                });

            }
        }).addTo(map);

        // Store the new layer reference and remove the old one
        if (currentParaBoundaryLayer) {
            map.removeLayer(currentParaBoundaryLayer);
        }
        currentParaBoundaryLayer = newLayer;

    });

    getWatershedWiseParaLegend(paraColor_info);

}

var storeCategoryWiseLayer = null;
var storeParaLabel = [];
function getCategoryWiseMap(category_id, category_val, getFilePath, layer_color, legend_info) {

    $.getJSON(getFilePath, function(geoJsonData) {

        var newLayer = L.geoJson(geoJsonData, {
            style: function(feature) {
                return {
                    color: 'black',
                    weight: '1',
                    opacity: 0.3,
                    fillColor: dynamicFillColor(layer_color, feature.properties, category_val),
                    fillOpacity: 0 
                };
            },
            onEachFeature: function(feature, layer) {
                
                var name = feature.properties.Para_Name;
                var center = [feature.properties.YCoor, feature.properties.XCoor];

                // Add the label at the center position
                const label = L.marker(center, {
                    icon: L.divIcon({
                        className: 'label',
                        html: `<div style="font-family: 'Cambria';">${name}</div>`
                    })
                }).addTo(map);

                storeParaLabel.push(label); // Track the label marker
                
                // var act_content;
                // var category_name;
                // layer_color.forEach(function(item) {
                //     if (item.para_name === name) {
                //         act_content = item.actual_content;
                //         category_name = item.cat_name;
                //     }
                // });

                layer.on('mouseover', function(event) {
                    // layer.getElement().style.cursor = 'cursor';
                    layer.setStyle({
                        weight: 2,
                        opacity: 0.7,
                        fillOpacity: 0.9
                    });
                });
    
                layer.on('mouseout', function(event) {
                    layer.setStyle({
                        weight: 1,
                        opacity: 0.3,
                        fillOpacity: 0.8
                    });
                });

                layer.on('click', function(event) {
                    var paraName = feature.properties.Para_Name;
                    
                    $('#content_title').html(paraName);
                    $('.tabular-div-popup').fadeIn('slow');

                    const communityTypeId = ['population', 'income', 'expense'];

                    const oneValueCategoryTypeId = [
                        'hazard', 'vulnerability', 'sensitivity', 'exposure', 'adaptive_capacity', 'climate_risk', 'agriculture', 'livestock', 'fisheries'
                    ];

                    if(communityTypeId.includes(category_val)) {
                        communityWiseTabulardata(category_id, paraName);
                    } else if (category_val == 'education') {
                        getEducationTabularData(paraName);
                    } else if (category_val == 'literacy') {
                        getLiteracyTabularData(paraName);
                    } else if (oneValueCategoryTypeId.includes(category_val)) {
                        getOneValueBasedTabularData(category_id, paraName);
                    }
                    
                    // Prevent map click event from hiding the popover immediately
                    event.originalEvent.stopPropagation();

                });
                
            }
        }).addTo(map);

        // Function to gradually increase the opacity of the layer
        function showLayerSlowly(layer) {
            var opacity = 0;
            var interval = setInterval(function() {
                opacity += 0.05; // Slower increment
                if (opacity >= 1) {
                    opacity = 1;
                    clearInterval(interval);
                }
                layer.setStyle({ fillOpacity: opacity });
            }, 200); // Increase interval duration
        }

        // Apply the slow showing effect to each feature
        newLayer.eachLayer(function(layer) {
            showLayerSlowly(layer);
        });

        // Store the new layer reference and remove the old one
        if (storeCategoryWiseLayer) {
            map.removeLayer(storeCategoryWiseLayer);
        }
        storeCategoryWiseLayer = newLayer;
    });

    getCategoryWiseLegend(legend_info);

}

function getCategoryWiseNaturalMap(category_id, category_val, getFilePath, layer_color, legend_info) {

    // Clear previous labels before creating new ones
    labelParaNames.forEach(label => map.removeLayer(label));
    labelParaNames = [];

    storeParaLabel.forEach(label => map.removeLayer(label));
    storeParaLabel = [];

    $.getJSON(getFilePath, function(geoJsonData) {

        var newLayer = L.geoJson(geoJsonData, {
            style: function(feature) {
                return {
                    color: 'black',
                    weight: '1',
                    opacity: 0.3,
                    fillColor: dynamicFillColor(layer_color, feature.properties, category_val),
                    fillOpacity: 0 
                };
            },
            onEachFeature: function(feature, layer) {

                layer.on('click', function(event) {
                    var title = '';
                    var attrValue = '';
                    var area = '';
                    var appendString = '';
                    
                    if (category_val == 'soil') {
                        title = 'Soil';
                        attrValue = feature.properties.Soil_Type;
                        appendString = `<tr><td>Soil Type</td><td>${attrValue}</td></tr>`;
                    } else if (category_val == 'slope') {
                        title = 'Slope';
                        attrValue = feature.properties.Percent_Slope;
                        appendString = `<tr><td>Percent Slope</td><td>${attrValue}</td></tr>`;
                    } else if (category_val == 'land_use') {
                        title = 'Land-use';
                        attrValue = feature.properties.Class;
                        area = feature.properties.Shape_Area;
                        appendString = `<tr><td>Class</td><td>${attrValue}</td></tr>
                                        <tr><td>Area</td><td>${area}</td></tr>`;
                    } else if (category_val == 'topography') {
                        title = 'Topography';
                        attrValue = feature.properties.Elevation;
                        area = feature.properties.Area_km2;
                        appendString = `<tr><td>Elevation</td><td>${attrValue}</td></tr>
                                        <tr><td>Area (km²)</td><td>${area}</td></tr>`;
                    } 
                
                    $('#content_title').html(title);
                    
                    // Clear previous table content
                    $('#table_body').empty();
                    
                    // Append new content
                    $('#table_body').append(appendString);
                    
                    $('.tabular-div-popup').fadeIn('slow');
                
                    // Prevent map click event from hiding the popover immediately
                    event.originalEvent.stopPropagation();
                });
                
            }
        }).addTo(map);

        // Function to gradually increase the opacity of the layer
        function showLayerSlowly(layer) {
            var opacity = 0;
            var interval = setInterval(function() {
                opacity += 0.05; // Slower increment
                if (opacity >= 1) {
                    opacity = 1;
                    clearInterval(interval);
                }
                layer.setStyle({ fillOpacity: opacity });
            }, 200); // Increase interval duration
        }

        // Apply the slow showing effect to each feature
        newLayer.eachLayer(function(layer) {
            showLayerSlowly(layer);
        });

        // Store the new layer reference and remove the old one
        if (storeCategoryWiseLayer) {
            map.removeLayer(storeCategoryWiseLayer);
        }
        storeCategoryWiseLayer = newLayer;
    });

    getCategoryWiseLegend(legend_info);

}

function communityWiseTabulardata(category_id, paraName) {

    $.ajax({
        type: "POST",
        url: "/get-community-wise-tabular-data/",
        headers: { "X-CSRFToken": csrftoken },
        data: { 'categry_id': category_id, 'para_name' : paraName },
        dataType: "json",
        cache: false,
        success: function (data) {
            console.log(data);
            if (data.response.length > 0) {
                const retData = data.response;
                let appendString = '';
                const itemStatus = {};
            
                $('#table_body').empty();
                $('#show_error').html('');
            
                appendString += createHeader(data.response, itemStatus);
                appendString += createRows(data.response, itemStatus);
            
                $('#table_body').append(appendString);
            } else {
                $('#table_body').empty();
                let appendString = `<h3 style="font-size: 15px; color: red; font-family: Cambria;"> Sorry, we tried but not data found in the record...</h3>`;
                $('#show_error').html(appendString);
            }
            
            function createHeader(details, itemStatus) {
                let headerString = '<tr style="background-color: #6bbfd9;">';
                headerString += '<th style="text-align: left; font-weight: bold;">Items</th>';
            
                $.each(details, function(index, item) {
                    $.each(item, function(key, value) {
                        if (key !== 'description' && key !== 'total' && !itemStatus[key]) {
                            headerString += `<th style="text-align: left; font-weight: bold;">${capitalizeFirstLetter(key)}</th>`;
                            itemStatus[key] = true;
                        }
                    });
                });
            
                headerString += '<th style="text-align: right !important; font-weight: bold;">Total</th>';
                headerString += '</tr>';
            
                return headerString;
            }
            
            function createRows(details, itemStatus) {
                let rowsString = '';
            
                $.each(details, function(index, item) {
                    rowsString += '<tr>';
                    rowsString += `<td style="text-align: left; ">${item.description}</td>`;
            
                    $.each(itemStatus, function(key, status) {
                        if (status) {
                            rowsString += `<td style="text-align: center;font-family: Times New Roman; ">${item[key] || 0}</td>`;
                        }
                    });
            
                    rowsString += `<td style="text-align: right;font-family: Times New Roman; ;">${item.total}</td>`;
                    rowsString += '</tr>';
                });
            
                return rowsString;
            }
            
        },
        error: function(xhr, ajaxOptions, thrownError) {
            console.log(thrownError + "\r\n" + xhr.statusText + "\r\n" + xhr.responseText);
        }
    });

}

function getEducationTabularData(paraName) {

    $.ajax({
        type: "POST",
        url: "/get-education-info/",
        headers: { "X-CSRFToken": csrftoken },
        data: { 'para_name' : paraName },
        dataType: "json",
        cache: false,
        success: function (data) {
            // console.log(data);
            if (data.response.length > 0) {
                let appendString = '';
                const itemStatus = {};
            
                $('#table_body').empty();
                $('#show_error').html('');
            
                appendString += createHeader(data.response, itemStatus);
                appendString += createRows(data.response, itemStatus);
            
                $('#table_body').append(appendString);
            } else {
                $('#table_body').empty();
                let appendString = `<h3 style="font-size: 15px; color: red; font-family: Cambria;"> Sorry, we tried but not data found in the record...</h3>`;
                $('#show_error').html(appendString);
            }
            
            function createHeader(details, itemStatus) {
                let headerString = '<tr style="background-color: #6bbfd9;">';
                headerString += '<th style="text-align: left;width: 50%;font-weight: bold;">Items</th>';
                // headerString += '<th style="text-align: center !important;width: 10%;font-weight: bold;">Ins_number</th>';
            
                $.each(details, function(index, item) {
                    $.each(item, function(key, value) {
                        if (key !== 'description' && key !== 'institution_number' && !itemStatus[key]) {
                            headerString += `<th style="text-align: left;width: 10%;font-weight: bold;">${key}</th>`;
                            itemStatus[key] = true;
                        }
                    });
                });
            
                headerString += '</tr>';
            
                return headerString;
            }
            
            function createRows(details, itemStatus) {
                let rowsString = '';
            
                $.each(details, function(index, item) {
                    rowsString += '<tr>';
                    rowsString += `<td style="text-align: left;font-family: Cambria;width: 50%;">${item.description}</td>`;
                    // rowsString += `<td style="text-align: center;font-family: Times New Roman;width: 10%;">${item.ins_num}</td>`;
            
                    $.each(itemStatus, function(key, status) {
                        if (status) {
                            rowsString += `<td style="text-align: center;font-family: Times New Roman;width: 10%;">${item[key] || 0}</td>`;
                        }
                    });
                    
                    rowsString += '</tr>';
                });
            
                return rowsString;
            }
            
        },
        error: function(xhr, ajaxOptions, thrownError) {
            console.log(thrownError + "\r\n" + xhr.statusText + "\r\n" + xhr.responseText);
        }
    });

}

function getLiteracyTabularData(paraName) {

    $.ajax({
        type: "POST",
        url: "/get-literacy-info/",
        headers: { "X-CSRFToken": csrftoken },
        data: { 'para_name' : paraName },
        dataType: "json",
        cache: false,
        success: function (data) {
            // console.log(data);
            if (data.response.length > 0) {
                let appendString = '';
                const itemStatus = {};
            
                $('#table_body').empty();
                $('#show_error').html('');
            
                appendString += createHeader(data.response, itemStatus);
                appendString += createRows(data.response, itemStatus);
            
                $('#table_body').append(appendString);
            } else {
                $('#table_body').empty();
                let appendString = `<h3 style="font-size: 15px; color: red; font-family: Cambria;"> Sorry, we tried but not data found in the record...</h3>`;
                $('#show_error').html(appendString);
            }
            
            function createHeader(details, itemStatus) {
                let headerString = '<tr style="background-color: #6bbfd9;">';
                headerString += '<th style="text-align: left;width: 50%;font-weight: bold;">Items</th>';
            
                $.each(details, function(index, item) {
                    $.each(item, function(key, value) {
                        if (key !== 'description' && key !== 'institution_number' && !itemStatus[key]) {
                            headerString += `<th style="text-align: left;width: 10%;font-weight: bold;">${capitalizeFirstLetter(key)}</th>`;
                            itemStatus[key] = true;
                        }
                    });
                });
            
                headerString += '</tr>';
            
                return headerString;
            }
            
            function createRows(details, itemStatus) {
                let rowsString = '';
            
                $.each(details, function(index, item) {
                    rowsString += '<tr>';
                    rowsString += `<td style="text-align: left;font-family: Cambria;width: 50%;">${item.description}</td>`;
            
                    $.each(itemStatus, function(key, status) {
                        if (status) {
                            rowsString += `<td style="text-align: center;font-family: Times New Roman;width: 10%;">${item[key] || 0}</td>`;
                        }
                    });
                    
                    rowsString += '</tr>';
                });
            
                return rowsString;
            }
            
        },
        error: function(xhr, ajaxOptions, thrownError) {
            console.log(thrownError + "\r\n" + xhr.statusText + "\r\n" + xhr.responseText);
        }
    });

}

function getOneValueBasedTabularData(catgry_id, paraName) {

    $.ajax({
        type: "POST",
        url: "/get-one-value-based-tabular-data/",
        headers: { "X-CSRFToken": csrftoken },
        data: { 'category_id': catgry_id, 'para_name' : paraName },
        dataType: "json",
        cache: false,
        success: function (data) {
            console.log(data);
            if (data.response.length > 0) {
                let appendString = '';
                const itemStatus = {};
            
                $('#table_body').empty();
                $('#show_error').html('');
            
                appendString += createHeader(data.response, itemStatus);
                appendString += createRows(data.response, itemStatus);
            
                $('#table_body').append(appendString);
            } else {
                $('#table_body').empty();
                let appendString = `<h3 style="font-size: 15px; color: red; font-family: Cambria;"> Sorry, we tried but not data found in the record...</h3>`;
                $('#show_error').html(appendString);
            }
            
            function createHeader(details, itemStatus) {
                let headerString = '<tr style="background-color: #6bbfd9;">';
                headerString += '<th style="text-align: left;width: 50%;font-weight: bold;">Description</th>';
            
                $.each(details, function(index, item) {
                    $.each(item, function(key, value) {
                        if (key !== 'description' && key !== 'institution_number' && !itemStatus[key]) {
                            headerString += `<th style="text-align: left;width: 10%;font-weight: bold;">${capitalizeFirstLetter(key)}</th>`;
                            itemStatus[key] = true;
                        }
                    });
                });
            
                headerString += '</tr>';
            
                return headerString;
            }
            
            function createRows(details, itemStatus) {
                let rowsString = '';
            
                $.each(details, function(index, item) {
                    rowsString += '<tr>';
                    rowsString += `<td style="text-align: left;font-family: Cambria;width: 50%;">${item.description}</td>`;
            
                    $.each(itemStatus, function(key, status) {
                        if (status) {
                            rowsString += `<td style="text-align: left;font-family: Times New Roman;width: 10%;">${item[key] || 0}</td>`;
                        }
                    });
                    
                    rowsString += '</tr>';
                });
            
                return rowsString;
            }
            
        },
        error: function(xhr, ajaxOptions, thrownError) {
            console.log(thrownError + "\r\n" + xhr.statusText + "\r\n" + xhr.responseText);
        }
    });

}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function dynamicFillColor(data, features, category_val) {
    let fillColor = '#000000';
    let attribute;

    switch (category_val) {
        case 'land_use':
            attribute = 'Class';
            break;
        case 'soil':
            attribute = 'Soil_Type';
            break;
        case 'slope':
            attribute = 'Percent_Slope';
            break;
        case 'topography':
            attribute = 'Elevation';
            break;
        default:
            attribute = 'Para_Name';
    }

    data.forEach(item => {
        if (item.para_name === features[attribute]) {
            fillColor = item.layer_color;
        }
        // console.log("here you..",item.para_name);
    });

    return fillColor;
}

function showDistrictMap (category_id, getShapeFilesPath, legendColor) {
    
    $.getJSON(getShapeFilesPath, function(geoJsonData) {
        
        var zoomThreshold = 8;
        function updateMapLayerLabel(layer, feature) {
            var currentZoom = map.getZoom();
            var MapTitle = feature.properties.District;
            
            if (currentZoom >= zoomThreshold) {
                if (!layer.getTooltip()) { 
                    layer.bindTooltip(MapTitle, { permanent: true, direction: 'top' }).openTooltip();
                }
            } else {
                if (layer.getTooltip()) { 
                    layer.unbindTooltip();
                }
            }
        }

        var newLayer = L.geoJson(geoJsonData.features, {
            style: function(feature) { 
                return {
                    color: legendColor,
                    weight: 2, 
                    opacity: 1,
                    fillColor: 'none', 
                    fillOpacity: '0'
                };
            },
            onEachFeature: function(feature, layer) {
                updateMapLayerLabel(layer, feature);
                map.on('zoomend', function() {
                    updateMapLayerLabel(layer, feature);
                });
            }
        }).addTo(map);

        layers[category_id] = newLayer;

        map.on('zoomend', function() {
            newLayer.eachLayer(function(layer) {
                updateMapLayerLabel(layer, layer.feature);
            });
        });
    });

}


// +--- Start :: Map Legend Function ---+

function initializeLegend(zilaColors) {
    $('#legend-items').empty();

    let legendHTML = '<div style="font-weight: bold; margin-bottom: 5px;">Districts</div>';
    
    // Add dynamic ZILA items
    if (zilaColors) {
        Object.entries(zilaColors).forEach(([zila, color]) => {
            legendHTML += `
            <div class="legend-item" style="display: flex; align-items: center; padding: 5px 0; font-size: 12px;">
                <div style="width: 25px; height: 15px; background-color: ${color}; 
                     margin-right: 8px; border-radius: 3px; opacity: 0.3;"></div>
                <span>${zila}</span>
            </div>`;
        });
    }
    
    $('#legend-items').append(legendHTML);
}

function getDistrictWiseWatershedLegend(districtAreas) {
    $('#legend-items').empty();
    
    let legendHTML = '<div style="font-weight: bold; margin-bottom: 5px;">Watersheds</div>';
    
    // Add the red-colored watershed codes
    if (districtAreas) {
        // Get the current district from the select element
        const currentDistrict = $('#district-select').val();
        
        if (currentDistrict && districtAreas[currentDistrict]) {
            districtAreas[currentDistrict].forEach(code => {
                legendHTML += `
                <div class="legend-item" style="display: flex; align-items: center; padding: 5px 0; font-size: 12px;">
                    <div style="width: 25px; height: 15px; background-color: red; 
                         margin-right: 8px; border-radius: 3px;"></div>
                    <span>${code}</span>
                </div>`;
            });
        }
    }
    
    $('#legend-items').append(legendHTML);
}

function getWatershedWiseParaLegend(paraColor_info) {
    $('#legend-items').empty();
    
    if (!paraColor_info || !Array.isArray(paraColor_info)) return;
    
    const title = paraColor_info.length > 0 ? paraColor_info[0].title_name : 'Watershed Para';
    
    let legendHTML = `<div style="font-weight: bold; margin-bottom: 5px;">${title}</div>`;
    
    paraColor_info.forEach(item => {
        legendHTML += `
        <div class="legend-item" style="display: flex; align-items: center; padding: 5px 0; font-size: 12px;">
            <div style="width: 25px; height: 15px; background-color: ${item.para_map_color || 'orange'}; 
                 margin-right: 8px; border-radius: 3px;"></div>
            <span>${item.para_name || ''}</span>
        </div>`;
    });
    
    $('#legend-items').append(legendHTML);
} 

function getCategoryWiseLegend(legend_data) {
    $('#legend-items').empty();
    
    if (!legend_data || !Array.isArray(legend_data)) return;
    
    const title = legend_data.length > 0 ? legend_data[0].title_name : 'Watershed Para';
    
    let legendHTML = `<div style="font-weight: bold; font-size: 13px; margin-bottom: 5px;">${title}</div>`;
    
    legend_data.forEach(item => {
        legendHTML += `
        <div class="legend-item" style="display: flex; align-items: center; padding: 5px 0; font-size: 12px;">
            <div style="width: 25px; height: 15px; background-color: ${item.legend_color || 'orange'}; 
                 margin-right: 8px; border-radius: 3px;"></div>
            <span>${item.legend_name || ''}</span>
        </div>`;
    });
    
    $('#legend-items').append(legendHTML);
}

let firstTimeAdd = true;

function updateLegend(action, legend_data) {
    if (!legend_data || legend_data.length === 0) {
        console.log("No legend data available.");
        return;
    }

    if (action === 'add') {
        if (firstTimeAdd) {
            $('#legend-items').empty();
            firstTimeAdd = false;
        }

        $.each(legend_data, function (index, item) {
            let title = item.title_name || "Untitled";
            let name = item.legend_name || "Unknown";
            let lineColor = item.legend_color || "#000";
            let legendId = `legend-${item.row_id}`;
            let titleId = `title-${title.replace(/\s+/g, '-')}`;

            // If the title doesn't exist, create a new section
            if ($(`#${titleId}`).length === 0) {
                $('#legend-items').append(
                    `<div id="${titleId}" class="legend-title-wrapper">
                        <div style="padding: 0 0 5px 0;"> 
                            <label style="margin-bottom: 0; font-size: 12px;">${title}</label> 
                        </div>
                    </div>`
                );
            }

            // Append legend item under the respective title
            if ($(`#${legendId}`).length === 0) {
                $(`#${titleId}`).append(
                    `<div id="${legendId}" class="legend-item" style="display: flex; align-items: center; padding: 0px 0px 5px 0px; font-size: 12px;">
                        <div style="width: 40px; height: 20px; background-color: ${lineColor}; margin-right: 5px; border-radius: 3px;"></div>
                        <span style="font-size: 12px;">&nbsp; ${name}</span>
                    </div>`
                );
            }
        });
    } 
    else if (action === 'remove') {
        $.each(legend_data, function (index, item) {
            let legendId = `legend-${item.row_id}`;
            let titleId = `title-${item.title_name.replace(/\s+/g, '-')}`;

            // Remove only the specific legend item
            if ($(`#${legendId}`).length > 0) {
                $(`#${legendId}`).remove();
            }

            // If no more items exist under this title, remove the title as well
            if ($(`#${titleId} .legend-item`).length === 0) {
                $(`#${titleId}`).remove();
            }
        });
    }
}

// +--- End :: Map Legend Function ---+

function clearAllLayer() {
   // Remove previous fill color layer if exists
    if (currentParaBoundaryLayer) {
        map.removeLayer(currentParaBoundaryLayer);
        currentParaBoundaryLayer = null;
    }

    // Clear previous labels before creating new ones
    labelParaNames.forEach(label => map.removeLayer(label));
    labelParaNames = [];

    // Remove previous fill color layer if exists
    if (currentWatershedFillLayer) {
        map.removeLayer(currentWatershedFillLayer);
        currentWatershedFillLayer = null;
    }

    // Clear previous labels before creating new ones
    storeParaLabel.forEach(label => map.removeLayer(label));
    storeParaLabel = [];

}

function fullExtendMap() {
    $("#fullExtendMap").on("click", function () {
        if (map) {
            mapCenter = mapCenter || [23.71466803926892, 90.582723353677];
            mapZoom = mapZoom || 7.5;
    
            map.flyTo(mapCenter, mapZoom, {
                duration: 2.5,  // Increased duration for smoother transition
                easeLinearity: 0.25,  // Adjusts the animation curve
                noMoveStart: false,  // Ensures animation starts immediately
                
                // These are the default flyTo options that create smooth animation:
                animate: true,
                zoom: {
                    animate: true,
                    duration: 1.5
                }
            });
        }
        clearAllLayer();
        getDivisionMap();
        getWatershedBoundaryMap();

    });   
}

function districtWiseCloseMap(dis_name) {

    const districtCenters = {
        'Rangamati': [23.0076298, 92.320122], 
        'Bandarban': [21.8013330, 92.51388221],
        'Khagrachhari': [23.2275978, 91.9779375],
        'default': [23.80466803926892, 90.583723353677],
    };
    
    // Default to Khagrachhari if district not found
    const mapCenter = districtCenters[dis_name] || districtCenters.default;
    const mapZoom = 9.5;
    
    // Smooth transition with enhanced animation parameters
    map.flyTo(mapCenter, mapZoom, {
        duration: 2,  // Increased duration for smoother transition
        easeLinearity: 0.1,  // Smoother easing curve
        essential: true,  // Ensures animation runs even in low-performance mode
        
        // Zoom animation settings
        zoom: {
            animate: true,
            duration: 2,
            easeLinearity: 0.1
        },
        
        // Rotation animation (optional)
        bearing: 0,
        pitch: 0,
        
        // Callbacks for animation events
        complete: function() {
            console.log('Map transition complete');
            // Add any post-animation effects here
        },
        error: function() {
            console.warn('Map transition interrupted');
        }
    });


}

function watershedWiseCloseMap(watershed_id) {
    const watershedConfig = {
        'R114': {
            center: [22.776853482, 92.0792251],
            zoom: 13.50
        },
        'R99': {
            center: [22.8796770246, 92.4216295481],
            zoom: 13
        },
        'R65': {
            center: [23.2187678134, 92.1779578467],
            zoom: 13.50
        },
        'B173': {
            center: [21.7886415106, 92.4704485575],
            zoom: 13.50
        },
        'B76': {
            center: [22.0284018797, 92.2501842217],
            zoom: 13.50
        },
        'B77': {
            center: [22.008296156, 92.2714579067],
            zoom: 14.25
        },
        'K98': {
            center: [23.3942906241, 91.8866576422],
            zoom: 13.75
        },
        'K76': {
            center: [23.3036675464, 92.0781291686],
            zoom: 13.25
        },
        'K71': {
            center: [23.2038232393, 91.9788753007],
            zoom: 13.25
        },
        'default': {
            center: [23.80466803926892, 90.583723353677],
            zoom: 12
        }
    };
    
    const config = watershedConfig[watershed_id] || watershedConfig.default;
    
    // Smooth transition with enhanced animation parameters
    map.flyTo(config.center, config.zoom, {
        duration: 4,               // Increased duration for smoother transition
        easeLinearity: 0.1,        // Smoother easing curve
        essential: true,           // Ensures animation runs even in low-performance mode
        
        // Zoom animation settings
        zoom: {
            animate: true,
            duration: 2,
            easeLinearity: 0.1
        },
        
        // Rotation animation (optional)
        bearing: 0,
        pitch: 0,
        
        // Callbacks for animation events
        complete: function() {
            console.log('Map transition complete');
            // Add any post-animation effects here
        },
        error: function() {
            console.warn('Map transition interrupted');
        }
    });
}

var wellZoomThreshold = 10;
function updateWatershedLabel(layer, feature) {
    var currentZoom = map.getZoom();
    var watershedCode = feature.properties.SL_NO;
    
    if (currentZoom >= wellZoomThreshold) {
        if (!layer.getTooltip()) {
            layer.bindTooltip(watershedCode, { 
                permanent: true, 
                direction: 'top', 
                offset: [0, -40] 
            }).openTooltip();
        }
    } else {
        if (layer.getTooltip()) {
            layer.unbindTooltip();
        }
    }
}


// 
function mapLayers () {

    // Change the map layer based on user selection
    $("#open-street").on('click', function(event) {
        event.preventDefault();
        map.eachLayer(function(layer) {
            map.removeLayer(layer);
        });
        openStreetLayer.addTo(map);
        getDivisionMap();
        getWatershedBoundaryMap();
    });

    $("#google-hybrid").on('click', function(event) {
        event.preventDefault();
        map.eachLayer(function(layer) {
            map.removeLayer(layer);
        });
        googleHybrid.addTo(map);
        getDivisionMap();
        getWatershedBoundaryMap();
    });

    $("#google-satellite").on('click', function(event) {
        event.preventDefault();
        map.eachLayer(function(layer) {
            map.removeLayer(layer);
        });
        googleSatelliteLayer.addTo(map);
        getDivisionMap();
        getWatershedBoundaryMap();
    });

    $("#google-street").on('click', function(event) {
        event.preventDefault();
        map.eachLayer(function(layer) {
            map.removeLayer(layer);
        });
        googleStreetLayer.addTo(map);
        getDivisionMap();
        getWatershedBoundaryMap();
    });

}

// +-- Start :: Different tile layers --+
var openStreetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: ''
});

var googleHybrid = L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', { 
    id: 'MapID', minZoom: 0, maxZoom: 25, 
    subdomains: ["mt0", "mt1", "mt2", "mt3"], 
    attribution: '' 
});

var googleSatelliteLayer = L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: ''
});

var googleStreetLayer = L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: ''
});
// +-- End :: Different tile layers --+
