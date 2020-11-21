// csrf setup
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function load_images(project_id) {
    let result = undefined;
    console.log("Loading image metadata for project " + project_id);
    $.ajax({
        url: '/api/image/',
        data: {project: project_id},
        type: 'GET',
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            result = data;
        },
        error: console.error,
        async: false,
    });
    return result;
}

function load_img_metadata(project_id) {
    let images = load_images(project_id);
    let image_id_list = [];
    let img_metadata = {};
    for (let i in images) {
        if (!images.hasOwnProperty(i)) continue;
        const id = images[i].filename + images[i].size;
        image_id_list.push(id);
        if (images[i].file_attributes === null) images[i].file_attributes = {};
        if (images[i].regions === null) images[i].regions = [];
        img_metadata[id] = images[i];
    }
    return {
        img_metadata: img_metadata,
        image_id_list: image_id_list
    }
}

function refresh_img_metadata(project_id) {
    console.time('refresh_img_metadata')
    if (typeof project_id === 'undefined') project_id = PROJECT_PK;
    let new_data = load_img_metadata(project_id);
    for (let i in new_data.image_id_list) {
        if (!new_data.image_id_list.hasOwnProperty(i)) continue;
        const img_id = new_data.image_id_list[i];
        if (new_data.img_metadata[img_id] !== undefined) {
            _via_img_metadata[img_id] = new_data.img_metadata[img_id];
            if (_via_image_id_list.indexOf(img_id) < 0) {
                _via_image_id_list.push(img_id);
            }
        }
    }
    console.timeEnd('refresh_img_metadata')
}

function load_project(project_id, error_callback) {
    if (typeof error_callback === 'undefined') error_callback = console.error;
    let metadata = load_img_metadata(project_id);
    let result = {
        _via_img_metadata: metadata['img_metadata'],
        _via_image_id_list: metadata['image_id_list'],
    };
    $.ajax({
        url: '/api/project',
        data: {pk: project_id},
        type: 'GET',
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            let project = data[0];
            if (project.settings === null) {
                project.settings = _via_settings;
            }
            if (project.attributes === null) {
                project.attributes = _via_attributes;
            }
            project.settings.project.name = PROJECT_NAME;
            result['_via_settings'] = project.settings;
            result['_via_attributes'] = project.attributes;
        },
        error: error_callback,
        async: false,
    });
    project_open_parse_json_file(JSON.stringify(result));
}

function save_image(image_id, no_refresh) {
    console.log("saving image with id", image_id);
    console.log("regions", _via_img_metadata[image_id].regions);
    let regions = [];
    for (let i = 0; i < _via_img_metadata[image_id].regions.length; i++) {
        regions.push(_via_img_metadata[image_id].regions[i]);
    }

    $.ajax({
        url: `/api/image/${_via_img_metadata[image_id].id}/`,
        data: JSON.stringify({
            regions: regions,
            file_attributes: _via_img_metadata[image_id].file_attributes,
        }),
        type: 'PATCH',
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        dataType: 'json',
        contentType: 'application/json',
        success: function () {
            show_message(`Image has been saved on server`);
            if (!no_refresh) refresh_img_metadata();
        },
        error: console.error,
    });
}

function upload_images(event) {
    let formData = new FormData();
    for(let i in event.target.files) {
        if (!event.target.files.hasOwnProperty(i)) continue;
        formData.append('images', event.target.files[i]);
    }
    formData.append('project', PROJECT_PK);
    $.ajax({
        url: `/api/image/`,
        type: 'POST',
        data: formData,
        cache: false,
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        contentType: false,
        processData: false,
        success: function(r) {
            show_message(`${event.target.files.length} images uploaded`);
            console.log("upload returned", r);
        },
        error: console.error
    });
    event.preventDefault();
    project_file_add_local(event);
}

function save_project() {
    $.ajax({
        url: `/api/project/${PROJECT_PK}/`,
        data: JSON.stringify({
            name: _via_settings.project.name,
            settings: _via_settings,
            attributes: _via_attributes,
        }),
        type: 'PATCH',
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        dataType: 'json',
        contentType: 'application/json',
        success: function () {
            show_message(`Project has been saved on server`);
        },
        error: function (d) {
            console.error(d);
            show_message(`ERROR during project save! Check js console`)
        },
    });
}