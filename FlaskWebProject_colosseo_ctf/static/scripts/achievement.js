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
// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

myChart.showLoading();    //数据加载完之前先显示一段简单的loading动画
$.ajax({
    type: "get",
    //       async : true,            //异步请求（同步请求将会锁住浏览器，用户其他操作必须等待请求完成才可以执行）
    url: "{{url_for('home_page.user_achievement_data',id=id)}}",    //请求发送到Servlet处
    //       data : {},
    dataType: "json",        //返回数据形式为json
    success: function (result) {
        myChart.hideLoading();
        myChart.setOption({ //加载数据图表
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
        //请求失败时执行该函数
        alert("wrong!");
        myChart.hideLoading();
    }
})