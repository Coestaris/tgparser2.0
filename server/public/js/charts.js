chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    random1: 'rgb(200, 66, 200)',
    grey: 'rgb(201, 203, 207)',
    random2: 'rgb(125, 222, 66)'
}

input_back_color = 'rgba(255, 99, 132, 0.6)'
input_color = 'rgba(255, 99, 132, 1)'
output_back_color = 'rgba(24, 147, 184, 0.6)'
output_color = 'rgba(52, 173, 209, 1)'

all_time_chart = null
time_chart = null
day_chart = null
month_chart = null
year_chart = null

input_media_chart = null
output_madia_chart = null

months = [
    'Январь', 'Февраль', 'Март',
    'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь',
    'Октябрь', 'Ноябрь', 'Декабрь'
]

function init_time_chart(input_data, output_data, labels) {
    const data = {
        labels: labels,
        datasets: [{
            label: 'Исходящих',
            data: output_data,
            backgroundColor: output_back_color,
            color: output_color,
            borderWidth: 1
        }, {
            label: 'Входящих',
            data: input_data,
            backgroundColor: input_back_color,
            color: input_color,
            borderWidth: 1
        }]
    };

    if (time_chart == null) {
        time_chart = new Chart(
            document.getElementById('chart-time').getContext('2d'), {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Распределение сообщений по часу суток'
                        },
                        scales: {
                            x: {
                                display: true,
                                offset: true,
                                title: {
                                    display: true,
                                    text: 'Hour'
                                },
                            }
                        }
                    }
                },
            });
    } else {
        time_chart.data = data
        time_chart.update()
    }
}

function init_day_chart(input_data, output_data) {
    const data = {
        labels: ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
        datasets: [{
            label: 'Исходящих',
            data: output_data,
            backgroundColor: output_back_color,
            color: output_color,
            borderWidth: 1
        }, {
            label: 'Входящих',
            data: input_data,
            backgroundColor: input_back_color,
            color: input_color,
            borderWidth: 1
        }]
    };

    if (day_chart == null) {
        day_chart = new Chart(
            document.getElementById('chart-day').getContext('2d'), {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Распределение сообщений по дням недели'
                        },
                    }
                },
            });
    } else {
        day_chart.data = data
        day_chart.update()
    }
}

function init_year_chart(input_data, output_data, labels) {
    const data = {
        labels: labels,
        datasets: [{
            label: 'Исходящих',
            data: output_data,
            backgroundColor: output_back_color,
            color: output_color,
            borderWidth: 1
        } , {
            label: 'Входящих',
            data: input_data,
            backgroundColor: input_back_color,
            color: input_color,
            borderWidth: 1
        }]
    };

    if (year_chart == null) {
        year_chart = new Chart(
            document.getElementById('chart-year').getContext('2d'), {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Распределение сообщений по годам'
                        },
                        scales: {
                            x: {
                                display: true,
                                offset: true,
                                title: {
                                    display: true,
                                    text: 'Год'
                                },
                            }
                        }
                    }
                },
            });
    } else {
        year_chart.data = data
        year_chart.update()
    }
}

function init_month_chart(input_data, output_data) {
    const data = {
        labels: months,
        datasets: [{
            label: 'Исходящих',
            data: output_data,
            backgroundColor: output_back_color,
            color: output_color,
            borderWidth: 1
        }, {
            label: 'Входящих',
            data: input_data,
            backgroundColor: input_back_color,
            color: input_color,
            borderWidth: 1
        }]
    };

    if (month_chart == null) {
        month_chart = new Chart(
            document.getElementById('chart-month').getContext('2d'), {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Распределение сообщений по месяцам'
                        },
                        scales: {
                            x: {
                                type: 'time',
                                display: true,
                                offset: true,
                                title: {
                                    display: true,
                                    text: 'month'
                                },
                                time: {
                                    unit: 'month'
                                }
                            }
                        }
                    }
                },
            });
    } else {
        month_chart.data = data
        month_chart.update()
    }
}

function init_all_time(input_data, output_data, labels) {
    let data = {
        labels: labels,
        datasets: [{
            label: 'Исходящих',
            data: input_data,
            backgroundColor: output_back_color,
            color: output_color,
            tension: 0.4,
            fill: true
        },
        {
            label: 'Входящих',
            data: output_data,
            backgroundColor: input_back_color,
            color: input_color,
            tension: 0.4,
            fill: true
        }]
    };


    if (all_time_chart == null) {
        all_time_chart = new Chart(
            document.getElementById('chart-all-time').getContext('2d'), {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Распределение сообщений за все время'
                        },
                        scales: {
                            x: {
                                type: 'time',
                                display: true,
                                title: {
                                    display: true,
                                    text: 'week',
                                },
                                time: {
                                    unit: 'week'
                                }
                            }
                        }
                    }
                },
            });
    } else {
        all_time_chart.data = data
        all_time_chart.update()
    }
}

function init_input_media_types(input, labels) {
    const data = {
        labels: labels,
        datasets: [{
            data: input,
            backgroundColor: Object.values(chartColors),
        }]
    };

    if (input_media_chart == null) {
        input_media_chart = new Chart(
            document.getElementById('chart-input-media-types').getContext('2d'), {
                type: 'pie',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Соотношение полученных медиа'
                        },
                    }
                },
            });
    } else {
        input_media_chart.data = data
        input_media_chart.update()
    }
}

function init_output_media_types(output, labels) {
    const data = {
        labels: labels,
        datasets: [{
            data: output,
            backgroundColor: Object.values(chartColors),
        }]
    };

    if (output_madia_chart == null) {
        output_madia_chart = new Chart(
            document.getElementById('chart-output-media-types').getContext('2d'), {
                type: 'pie',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Соотношение отправленных медиа'
                        },
                    }
                },
            });
    } else {
        output_madia_chart.data = data
        output_madia_chart.update()
    }
}