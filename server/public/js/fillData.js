function prettifySeconds(sec_num) {
    var years   = Math.floor(sec_num / 31556952);
    var days   = Math.floor((sec_num - (years * 31556952)) / 86400);
    var hours   = Math.floor((sec_num - (days * 86400) - (years * 31556952)) / 3600);

    let str = ''
    if (Math.floor(years) !== 0) {
        let prefix = ''
        switch (years) {
            case 1: prefix = 'год'; break;
            case 2:
            case 3:
            case 4: prefix = 'года'; break;
            case 5:
            case 6:
            case 7:
            case 8:
            case 9: prefix = 'лет'; break;
        }
        str += years + ' ' + prefix + ' '
    }
    if (Math.floor(days) !== 0) {
        if (hours == 0) {
            str += ' и '
        }
        let prefix = ''
        if (days > 10 && days < 20) {
            prefix = 'дней'
        } else {
            switch (Math.floor(days) % 10) {
                case 0: prefix = 'дней'; break;
                case 1: prefix = 'день'; break;
                case 2:
                case 3:
                case 4: prefix = 'дня'; break;
                case 5:
                case 6:
                case 7:
                case 8:
                case 9: prefix = 'дней'; break;
            }
        }
        str += days + ' ' + prefix
    }
    if (Math.floor(hours) !== 0) {
        str += ' и '
        let prefix = ''
        if (hours > 10 && hours < 20) {
            prefix = 'часов'
        } else {
            switch (Math.floor(hours) % 10) {
                case 0: prefix = 'часов'; break;
                case 1: prefix = 'час'; break;
                case 2:
                case 3:
                case 4: prefix = 'часа'; break;
                case 5:
                case 6:
                case 7:
                case 8:
                case 9: prefix = 'часов'; break;
            }
        }
        str += hours + ' ' + prefix
    }
    return str;
}

function prettifyMediaType(type) {
    switch (type) {
        case 'voice': return 'Аудио-сообщение'
        case 'plain': return 'Без медиа'
        case 'location': return 'Геолокация'
        case 'liveLocation': return 'Лайв-локация'
        case 'video': return 'Видео'
        case 'image': return 'Изображение'
        case 'videoMessage': return 'Видео-сообщение'
        case 'sticker': return 'Стикер'
        case 'audio': return 'Аудио'
    }
    return type
}

function prettifyChatType(type) {
    switch (type) {
        case 'saved_messages': return 'Избранные сообщения'
        case 'personal_chat': return 'Личный чат'
        case 'private_supergroup': return 'Приватная супер-группа'
        case 'private_group': return 'Приватная группа'
        case 'public_supergroup': return 'Публичная супер-группа'
        case 'public_group': return 'Публичная группа'
        case 'public_channel': return 'Публичный Онал'
        case 'private_channel': return 'Приватный канал'
    }
    return type
}

requests = []

function register_post_data(request, data, fn) {
    requests.push({
        'request': request,
        'fn': fn,
        'data': data,
        'status': false
    })
}

function update_progress_bars(index, status) {
    $('#progress-list').find('span').eq(index)
        .text('200 OK')
        .removeClass('bg-secondary')
        .addClass('bg-success')
    requests[index]['status'] = true

    let filtered = requests.filter(req => req['status'] === true)
    $('.progress-bar').css('width', (filtered.length / requests.length * 100) + '%')


    if(filtered.length === requests.length)
    {
        $('#loader').hide()
        $('#data').fadeIn(500)

        new Promise(resolve => setTimeout(resolve, 1000)).then(() => {
            $('.progress').addClass('visually-hidden')
            $('.progress-bar').css('width', '0%')
        })
    }
}

function do_post_data() {
    $('.progress-bar')
        .show()
        .attr('aria-valuemin', 0)
        .attr('aria-valuenow', 0)
        .css('width', 0)
        .attr('aria-valuemax', requests.length)

    $('#progress-list').empty()

    for (let p of requests)
        $('#progress-list')
            .append($('<li/>')
                .addClass('list-group-item')
                .addClass('d-flex')
                .addClass('justify-content-between')
                .addClass('align-items-start')
                .append($('<div/>')
                    .addClass('me-auto')
                    .text(p['request']))
                .append($('<span>')
                    .addClass('badge')
                    .addClass('bg-secondary')
                    .addClass('ms-3')
                    .addClass('rounded-pill')
                    .text('working')))

    for(let i = 0; i < requests.length; i++) {
        post(requests[i]['request'], requests[i]['data']).then((data) => {
            requests[i]['fn'](data)
            update_progress_bars(i, true)
        }).catch(() => {
            update_progress_bars(i, false)
        })
    }
}

personal_name = ""

function fill_base_info(data) {
    $("#personals-first-name").text(data.first_name)
    if(data.last_name === "null") {
        $("#personals-last-name").hide()
    } else {
        $("#personals-last-name").text(data.last_name)
    }
    if(data.bio === "null") {
        $("#personals-bio-row").hide()
        $("#personals-separator-row").hide()
    } else {
        $("#personals-bio").text(data.bio)
    }
    $("#personals-phone-number").text(data.phone_number)
    if(data.username === "null") {
        $("#personals-username-div").hide()
    } else {
        $("#personals-username").text(data.username)
    }
    $("#personals-user-id").text('#' + data.user_id)

    personal_name = data['first_name'] + (data['last_name'] !== "null" ? ' ' + data['last_name'] : '')
}

function fill_profile_pictures(data) {
    $("#main-profile-photo").attr('src',"data:image/jpg;base64, " + data[0].data);

    $("#modal-close").click(() => {
        $("#main-navbar").show()
        $("#modal-container").hide()
    })

    $(document).mouseup(function(e)
    {
        let container = $("#modal-image");
        if (!container.is(e.target) && container.has(e.target).length === 0) {
            $("#main-navbar").show()
            $("#modal-container").hide();
        }
    });

    for (let i = 1; i < data.length; i++) {
        let image_data = "data:image/jpg;base64, " + data[i].data

        let image_date = data[i].date.split('T')[0]
        let image_time = data[i].date.split('T')[1]

        let image = $('<img/>')
            .addClass('row-photo')
            .addClass('popup-image')
            .attr('src', image_data)
            .attr('alt', 'Установленно ' + image_date + ' ' + image_time)

        let div = $('<div/>')
            .append(image)
            .append($('<span/>')
                .text(image_date)
                .addClass('row-photo-label'))
            .addClass('row-photo-container')
        $("#sub-images-row")
            .append(div);
    }

    $(".popup-image").click((e) => {
        $("#main-navbar").hide()
        $("#modal-container").css('display', 'block');
        $("#modal-image").attr('src', $(e.target).attr('src'))
        $("#modal-caption").text($(e.target).attr('alt'))
    })
}

function fill_generals(data) {
    $('#time-in-telegram').text(prettifySeconds(parseFloat(data['from_first_message'])))
    $('#messages-in-day').text(data['messages_in_day'].toFixed(2))
    $('#total-sent').text(data['total_sent'])
    $('#total-received').text(data['total_received'])
}

function fill_all_time_chart(data) {
    let input = data['input']
    let outputs = data['output']
    let dates = []

    for(let key of data['keys']) {
        let year = Math.floor(key / 100)
        let week = key % 100

        let sunday = new Date(year, 0, (1 + (week - 1) * 7));
        while (sunday.getDay() !== 0) {
            sunday.setDate(sunday.getDate() - 1);
        }
        dates.push(months[sunday.getMonth()] + ' ' + sunday.getUTCDate() + ', ' + sunday.getFullYear())
    }

    init_all_time(input, outputs, dates)
}

function sortJson(dict) {
    var items = Object.keys(dict).map(function(key) {
        return [key, dict[key]];
    });

    items.sort(function(first, second) {
        return second[1] - first[1];
    });

    return items
}

text_data = {}

function fill_text_tables(words, mats, emoji) {
    if (words) {
        fill_text_table('#table-text-output', text_data['output_words'], 'inherit', '#words-count')
        fill_text_table('#table-text-input', text_data['input_words'], 'inherit', '#words-count')
    }
    if (mats) {
        fill_text_table('#table-mats-output', text_data['output_mats'], 'inherit', '#mats-count')
        fill_text_table('#table-mats-input', text_data['input_mats'], 'inherit', '#mats-count')
    }
    if (emoji) {
        fill_text_table('#table-emoji-output', text_data['output_emoji'], 'serif', '#emoji-count')
        fill_text_table('#table-emoji-input', text_data['input_emoji'], 'serif', '#emoji-count')
    }
}

function fill_text_table(query, data, font_family, max_source) {
    $(query).empty()
    let total_count = data['total']
    let words = data['dict']
    let counter = 1
    let max = parseInt($(max_source).val())

    for (const [key, value] of sortJson(words)) {
        if (counter === max + 1)
            break

        $(query).append($('<tr/>')
            .append($('<th/>')
                .attr('scope', 'row')
                .text(counter++))
            .append($('<td>')
                .css('font-family', font_family)
                .text(key))
            .append($('<td>')
                .text(value))
            .append($('<td>')
                .text((value / total_count * 100).toFixed(2) + '%')))
    }
}

function fill_text(data) {
    text_data = data

    fill_text_tables(true, true, true)

    $('#words-output').text(data['words_in_output'].toFixed(2))
    $('#words-input').text(data['words_in_input'].toFixed(2))

    $('#hello-output').text(data['hello_output'])
    $('#hello-input').text(data['hello_input'])
    $('#edited-output').text(data['edited_output'])
    $('#edited-input').text(data['edited_input'])
    $('#self-output').text(data['self_destruct_output'])
    $('#self-input').text(data['self_destruct_input'])
    $('#bots-output').text(data['via_bot_output'])
    $('#bots-input').text(data['via_bot_input'])
    $('#reply-output').text(data['replies_output'])
    $('#reply-input').text(data['replies_input'])
    $('#forward-output').text(data['forwarded_output'])
    $('#forward-input').text(data['forwarded_input'])

    $('#emoji-output').text(data['output_emoji']['total'])
    $('#emoji-input').text(data['input_emoji']['total'])

    $('#mats-output').text(data['output_mats']['total'])
    $('#mats-input').text(data['input_mats']['total'])

    let sticker_output = sortJson(data['output_stickers']['dict'])[0]
    sticker_output = sticker_output[0] + sticker_output[1] + ' раза'
    $('#sticker-output').text(sticker_output)

    let sticker_input = sortJson(data['input_stickers']['dict'])[0]
    sticker_input = sticker_input[0] + sticker_input[1] + ' раза'
    $('#sticker-input').text(sticker_input)
}

function fill_time_charts(data) {
    let hour_data = data['hour']
    init_time_chart(hour_data['input'], hour_data['output'], hour_data['keys'].map((el) => parseInt(el) + 1))

    let day_of_week_data = data['day_of_week']
    init_day_chart(day_of_week_data['input'], day_of_week_data['output'])

    let month_data = data['month']
    init_month_chart(month_data['input'], month_data['output'])

    let year_data = data['year']
    init_year_chart(year_data['input'], year_data['output'], year_data['keys'])
}

global_chats = {}

function fill_chats_table() {
    let max_count = $('#chats-count').val()

    if(max_count === 'Все')
        max_count = NaN
    else
        max_count = parseInt(max_count)

    $('#chats-table').empty()

    let counter = 1

    for(let chat of global_chats) {
        if (chat['messages_count'] === 0)
            break
        if (counter === max_count + 1)
            break
        $('#chats-table')
            .append($('<tr/>')
                .append($('<th/>')
                    .attr('scope', "row")
                    .text(counter++))
                .append($('<td/>')
                    .text(chat['name']))
                .append($('<td/>')
                    .append($('<span/>')
                        .addClass('text-muted')
                        .text('#id' + chat['id'])))
                .append($('<td/>')
                    .text(prettifyChatType(chat['type'])))
                .append($('<td/>')
                    .text(chat['messages_count'])))
    }
}

function fill_chats(data) {
    global_chats = data

    $('#chat-selection').empty()

    for(let chat of data)
        $('#chat-selection').append($('<option/>').text(chat['name']))

    fill_chats_table()
    update_filters()
}

function fill_misc(data) {
    let freq = data['freq_contacts']
    let installed = data['installed_stickers']
    let created = data['created_stickers']
    let ips = data['ips']
    let counter = 1

    for(let contact of freq) {
        if (counter === 30)
            break

        $('#freq-contacts-table')
            .append($('<tr/>')
                .append($('<th/>')
                    .attr('scope', "row")
                    .text(counter++))
                .append($('<td/>')
                    .text(contact['name']))
                .append($('<td/>')
                    .text('Пользователь'))
                .append($('<td/>')
                    .text(contact['rating'])))
    }

    counter = 1

    for(let sticker of installed) {
        $('#installed-sticker-table')
            .append($('<tr/>')
                .append($('<th/>')
                    .attr('scope', "row")
                    .text(counter++))
                .append($('<td/>')
                    .append($('<a/>')
                        .attr('href', sticker)
                        .text(sticker.split('/').pop()))))
    }
    counter = 1

    for(let sticker of created) {
        $('#created-stickers-table')
            .append($('<tr/>')
                .append($('<th/>')
                    .attr('scope', "row")
                    .text(counter++))
                .append($('<td/>')
                    .append($('<a/>')
                        .attr('href', sticker)
                        .text(sticker.split('/').pop()))))
    }
    counter = 1

    for(let ip of ips) {
        $('#ips-table')
            .append($('<tr/>')
                .append($('<th/>')
                    .attr('scope', "row")
                    .text(counter++))
                .append($('<td/>')
                    .append($('<a/>')
                        .attr('href', 'https://www.ip2location.com/demo/' + ip)
                        .text(ip))))
    }
}

function fill_media_charts(data) {
    let keys = data['keys']
    let input_data = data['input']
    let output_data = data['output']

    init_input_media_types(input_data, keys.map(prettifyMediaType))
    init_output_media_types(output_data, keys.map(prettifyMediaType))

    $('#calls-count').text(data['calls'])
    $('#calls-duration').text(data['calls_duration'].toFixed(2))
    $('#video-input-duration').text(data['video_input_duration'].toFixed(2))
    $('#video-output-duration').text(data['video_output_duration'].toFixed(2))
    $('#audio-input-duration').text(data['audio_input_duration'].toFixed(2))
    $('#audio-output-duration').text(data['audio_output_duration'].toFixed(2))
    $('#image-x-size').text(data['image_size'][0].toFixed(2))
    $('#image-y-size').text(data['image_size'][1].toFixed(2))
    $('#voice-input-duration').text(data['voice_input_duration'].toFixed(2))
    $('#voice-output-duration').text(data['voice_output_duration'].toFixed(2))
    $('#video-voice-input-duration').text(data['video_voice_input_duration'].toFixed(2))
    $('#video-voice-output-duration').text(data['video_voice_output_duration'].toFixed(2))
    $('#links-input').text(data['links_input'])
    $('#links-output').text(data['links_output'])

}

function update_filters() {
    checked = $('#select-chat').is(":checked")

    $('#allow-personals').attr('disabled', checked)
    $('#allow-private-chats').attr('disabled', checked)
    $('#allow-public-chats').attr('disabled', checked)
    $('#allow-publics').attr('disabled', checked)
    $('#allow-bots').attr('disabled', checked)

    cookie = JSON.parse($.cookie('filter_state'))
    $('#chat-selection').attr('disabled', !checked).val(cookie['selected_chat'])

    update_members()

    $('#member-selection').attr('disabled', !checked).val(cookie['selected_member'])
}

function update_members() {
    let val = $('#chat-selection').val()
    for(let chat of global_chats) {
        if(chat['name'] === val) {
            $('#member-selection')
                .empty()
                .append($('<option/>').text('Все пользователи'))
            for(let member of chat['members']) {
                if (member !== personal_name)
                    $('#member-selection')
                        .append($('<option/>').text(member))
            }
            return
        }
    }
}

function set_checkboxes(data) {
    $('#select-chat').attr('checked', data['chat'])

    $('#allow-personals').attr('checked', data['personals'])
    $('#allow-private-chats').attr('checked', data['private_chats'])
    $('#allow-public-chats').attr('checked', data['public_chats'])
    $('#allow-publics').attr('checked', data['channels'])
    $('#allow-bots').attr('checked', data['bots'])
}

function create_filter_package() {
    selecting_chat = $('#select-chat').is(":checked")
    selected_chat = $('#chat-selection').val()
    selected_member = $('#member-selection').val()

    data = {
        'personals': $('#allow-personals').is(":checked"),
        'private_chats': $('#allow-private-chats').is(':checked'),
        'public_chats': $('#allow-public-chats').is(':checked'),
        'channels': $('#allow-publics').is(':checked'),
        'bots': $('#allow-bots').is(':checked'),
        'chat': selecting_chat,
        'selected_chat': selected_chat,
        'selected_member': selected_member,
    }
    $.cookie('filter_state', JSON.stringify(data))
    return data
}

function recalc_all(filter_package) {
    requests = []
    initial_start = filter_package

    $('.progress').removeClass('visually-hidden')

    if(!initial_start) {
        filter_package = create_filter_package()
    }
    else {
        $('#loader').show()
        $('#data').hide()
        set_checkboxes(filter_package = JSON.parse(filter_package))
    }
    console.log(filter_package)

    if(initial_start) {
        register_post_data('/api/get_base_info', {}, fill_base_info)
        register_post_data('/api/get_profile_pictures', {}, fill_profile_pictures)
        register_post_data('/api/get_chats', {}, fill_chats)
        register_post_data('/api/get_misc', {}, fill_misc)
    }
    register_post_data('/api/get_generals', filter_package, fill_generals)
    register_post_data('/api/get_charts_all_time', filter_package, fill_all_time_chart)
    register_post_data('/api/get_charts_time', filter_package, fill_time_charts)
    register_post_data('/api/get_text', filter_package, fill_text)
    register_post_data('/api/get_charts_media', filter_package, fill_media_charts)

    do_post_data()
}

$(document).ready(function () {
    $('#select-chat').on('change', update_filters)
    $('#chats-count').on('change', fill_chats_table)
    $('#words-count').on('change', () => fill_text_tables(true, false, false))
    $('#mats-count').on('change', () => fill_text_tables(false, true, false))
    $('#emoji-count').on('change', () => fill_text_tables(false, false, true))

    $('#chat-selection').on('change', update_members)

    $('#recalc-btn').click(() => {
        recalc_all(undefined)
    })

    recalc_all($.cookie('filter_state'))
})
