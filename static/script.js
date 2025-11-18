let currentCoin = "bitcoin";
let chart = null;
let lineSeries = null;
let ema20Series = null;
let ema50Series = null;

function createChart(){
    const container = document.getElementById("chart");
    container.innerHTML = "";
    chart = LightweightCharts.createChart(container, {
        width: container.clientWidth,
        height: 420,
        layout: {
            backgroundColor: getComputedStyle(document.body).getPropertyValue('--bg'),
            textColor: getComputedStyle(document.body).getPropertyValue('--text')
        },
        grid: { vertLines:{color:'rgba(120,120,120,0.06)'}, horzLines:{color:'rgba(120,120,120,0.06)'}}
    });
    lineSeries = chart.addLineSeries({lineWidth:2, color:'#22c55e'});
    ema20Series = chart.addLineSeries({lineWidth:1, color:'#3b82f6'});
    ema50Series = chart.addLineSeries({lineWidth:1, color:'#f97316'});
    window.addEventListener('resize', ()=>chart.applyOptions({width:container.clientWidth}));
}

async function loadCoin(coinId, days){
    const res = await fetch(`/api/coin/${coinId}?days=${days}`);
    const data = await res.json();
    
    lineSeries.setData(data.prices);
    ema20Series.setData(data.ema20);
    ema50Series.setData(data.ema50);

    document.getElementById("coinTitle").textContent = coinId.toUpperCase();
    document.getElementById("lastPrice").textContent = "$"+data.last_price.toFixed(2);
    document.getElementById("trend").textContent = data.trend;
    document.getElementById("strength").textContent = data.strength;
}

document.querySelectorAll(".btn--interval").forEach(btn=>{
    btn.addEventListener("click", ()=>{
        document.querySelectorAll(".btn--interval").forEach(x=>x.classList.remove("btn--active"));
        btn.classList.add("btn--active");
        loadCoin(currentCoin, btn.getAttribute("data-days"));
    });
});

window.addEventListener("load", ()=>{
    createChart();
    loadCoin(currentCoin, 1);
});
