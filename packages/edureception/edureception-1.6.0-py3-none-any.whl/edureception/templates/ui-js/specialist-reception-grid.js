function specalistScheduleColumnRenderer(value, metaData, record, rowIndex, colIndex, store) {

    if (value['record_id'] === undefined) {
        display = '<span style="color:gray">' + value + '<span>';
    } else {
        var location = '';
        if (value['office']['location'] != undefined) {
            location = ' (' + value['office']['location'] +')';
        }
        display = '<div style="color:#0000CD"><b>' + value['begin'] + ' - '+ value['end'] + '</b></div>' +
                  '<div style="color:#006400">' + 'Каб.№' + value['office']['number'] + location + '</div>'

        if (value['fullname'] != undefined) {
            display = display +
                    '<div style="font-size:13px">' + value['fullname'] + '</div>'
        }
    }
    return display
}
