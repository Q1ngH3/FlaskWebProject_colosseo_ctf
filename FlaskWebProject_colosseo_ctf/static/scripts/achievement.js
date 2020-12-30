// Build the chart
var myChart = echarts.init(document.getElementById('container'));
var option = {
    title: {
        text: 'My Achievement',
        subtext: '',
        x: 'center'
    },
    tooltip: {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    legend: {
        orient: 'vertical',
        left: 'left',
        data: ['WEB', 'PWN', 'MISC', 'REV', 'CRYPTO']
    },
    series: [
        {
            name: 'Number',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: [],
            itemStyle: {
                emphasis: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 1.0)'
                }
            }
        }
    ]
};
// ʹ�ø�ָ�����������������ʾͼ��
myChart.setOption(option);

myChart.showLoading();    //���ݼ�����֮ǰ����ʾһ�μ򵥵�loading����
$.ajax({
    type: "get",
    //       async : true,            //�첽����ͬ�����󽫻���ס��������û�������������ȴ�������ɲſ���ִ�У�
    url: "{{url_for('home_page.user_achievement_data',id=id)}}",    //�����͵�Servlet��
    //       data : {},
    dataType: "json",        //����������ʽΪjson
    success: function (result) {
        myChart.hideLoading();
        myChart.setOption({ //��������ͼ��
            series: [{
                data: [
                    { value: result["data"][0]["value"], name: 'WEB' },
                    { value: result["data"][1]["value"], name: 'PWN' },
                    { value: result["data"][2]["value"], name: 'MISC' },
                    { value: result["data"][3]["value"], name: 'REV' },
                    { value: result["data"][4]["value"], name: 'CRYPTO' }
                ],
            }]
        });
    },
    error: function (errorMsg) {
        //����ʧ��ʱִ�иú���
        alert("wrong!");
        myChart.hideLoading();
    }
})