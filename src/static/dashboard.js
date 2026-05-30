document.addEventListener("DOMContentLoaded", async () => {
  const dateSelect = document.getElementById("dateSelect");
  const startInput = document.getElementById("startDate");
  const endInput = document.getElementById("endDate");
  const applyBtn = document.getElementById("applyRange");

  const topCtx = document.getElementById("topKeywordsChart").getContext("2d");
  let topChart = new Chart(topCtx, {
    type: "bar",
    data: { labels: [], datasets: [{ label: "Count", data: [] }] },
    options: { responsive: true }
  });

  const sentCtx = document.getElementById("sentimentChart").getContext("2d");
  let sentimentChart = new Chart(sentCtx, {
    type: "line",
    data: { labels: [], datasets: [{ label: "Average sentiment", data: [], fill: false, borderColor: 'rgb(75, 192, 192)' }] },
    options: { responsive: true }
  });

  const averagePriceSummary = document.getElementById("averagePriceSummary");
  const avgByDayCtx = document.getElementById("averagePriceByDayChart").getContext("2d");
  let avgByDayChart = new Chart(avgByDayCtx, {
    type: "line",
    data: { labels: [], datasets: [] },
    options: { responsive: true }
  });
  const avgByTickerCtx = document.getElementById("averagePriceByTickerChart").getContext("2d");
  let avgByTickerChart = new Chart(avgByTickerCtx, {
    type: "bar",
    data: { labels: [], datasets: [{ label: "Avg close price", data: [], backgroundColor: 'rgba(255, 159, 64, 0.7)' }] },
    options: { responsive: true }
  });

  const sentimentCountCtx = document.getElementById("sentimentCountChart").getContext("2d");
  let sentimentCountChart = new Chart(sentimentCountCtx, {
    type: "bar",
    data: { labels: [], datasets: [] },
    options: { responsive: true, scales: { x: { stacked: true }, y: { stacked: true } } }
  });

  function isoToDDMMYYYY(iso) {
    if (!iso) return '';
    const [y, m, d] = iso.split('-');
    return `${d}-${m}-${y}`;
  }

  async function fetchAndRenderTop(startISO, endISO) {
    const params = [];
    if (startISO) params.push(`start_date=${isoToDDMMYYYY(startISO)}`);
    if (endISO) params.push(`end_date=${isoToDDMMYYYY(endISO)}`);
    const url = `/api/top_keywords_by_day${params.length ? '?' + params.join('&') : ''}`;
    const resp = await fetch(url);
    const data = await resp.json();
    const byDay = data.top_keywords_by_day || {};

    // populate select
    dateSelect.innerHTML = '';
    const dates = Object.keys(byDay).sort();
    dates.forEach(d => {
      const opt = document.createElement('option');
      opt.value = d;
      opt.text = d;
      dateSelect.appendChild(opt);
    });

    function renderTopForDate(d) {
      const entries = byDay[d] || [];
      const labels = entries.map(e => Array.isArray(e) ? e[0] : (e[0] || e));
      const vals = entries.map(e => Array.isArray(e) ? e[1] : (e[1] || 0));
      topChart.data.labels = labels;
      topChart.data.datasets[0].data = vals;
      topChart.update();
    }

    if (dates.length) {
      renderTopForDate(dates[0]);
      dateSelect.value = dates[0];
    } else {
      topChart.data.labels = [];
      topChart.data.datasets[0].data = [];
      topChart.update();
    }

    dateSelect.onchange = (e) => renderTopForDate(e.target.value);
  }

  async function fetchAndRenderSentiment(startISO, endISO) {
    const params = [];
    if (startISO) params.push(`start_date=${isoToDDMMYYYY(startISO)}`);
    if (endISO) params.push(`end_date=${isoToDDMMYYYY(endISO)}`);
    const url = `/api/sentiment_by_day${params.length ? '?' + params.join('&') : ''}`;
    const resp = await fetch(url);
    const data = await resp.json();
    const sentByDay = data.sentiment_by_day || {};
    const sDates = Object.keys(sentByDay).sort();
    const sValues = sDates.map(d => sentByDay[d]);

    sentimentChart.data.labels = sDates;
    sentimentChart.data.datasets[0].data = sValues;
    sentimentChart.update();
  }

  applyBtn.addEventListener('click', async () => {
    const startISO = startInput.value || null;
    const endISO = endInput.value || null;
    await fetchAndRenderTop(startISO, endISO);
    await fetchAndRenderSentiment(startISO, endISO);
    await fetchAndRenderAveragePrice(startISO, endISO);
    await fetchAndRenderSentimentCounts(startISO, endISO);
  });

  // Initial load
  await fetchAndRenderTop();
  await fetchAndRenderSentiment();
  await fetchAndRenderAveragePrice();
  await fetchAndRenderSentimentCounts();

  // Correlation
  const corrResp = await fetch("/api/correlation");
  const corrData = await corrResp.json();
  document.getElementById("correlationReport").textContent = JSON.stringify(corrData, null, 2);

  async function fetchAndRenderAveragePrice(startISO, endISO) {
    const params = [];
    if (startISO) params.push(`start_date=${isoToDDMMYYYY(startISO)}`);
    if (endISO) params.push(`end_date=${isoToDDMMYYYY(endISO)}`);
    const url = `/api/average_oil_price${params.length ? '?' + params.join('&') : ''}`;
    const resp = await fetch(url);
    const data = await resp.json();
    const avg = data.average_price || {};
    if (!avg || avg.overall === null) {
      averagePriceSummary.textContent = "No average oil price data available for the selected range.";
      avgByDayChart.data.labels = [];
      avgByDayChart.data.datasets[0].data = [];
      avgByDayChart.update();
      avgByTickerChart.data.labels = [];
      avgByTickerChart.data.datasets[0].data = [];
      avgByTickerChart.update();
      return;
    }

    const byTicker = avg.by_ticker || {};
    let html = `<p><strong>Overall average close price:</strong> ${avg.overall.toFixed(2)}</p>`;
    html += '<ul>';
    Object.entries(byTicker).forEach(([ticker, value]) => {
      html += `<li>${ticker}: ${value.toFixed(2)}</li>`;
    });
    html += '</ul>';
    averagePriceSummary.innerHTML = html;

    const dailyTickerAverage = avg.daily_ticker_average || {};
    const dayLabels = Object.keys(dailyTickerAverage).sort((a, b) => {
      const [da, ma, ya] = a.split('-');
      const [db, mb, yb] = b.split('-');
      return new Date(`${ya}-${ma}-${da}`) - new Date(`${yb}-${mb}-${db}`);
    });

    const tickerColors = {
      'CL=F': 'rgb(54, 162, 235)',
      'BZ=F': 'rgb(255, 159, 64)',
      'NG=F': 'rgb(75, 192, 192)'
    };

    const tickers = Array.from(new Set(dayLabels.flatMap(day => Object.keys(dailyTickerAverage[day] || {})))).sort();
    const datasets = tickers.map((ticker) => ({
      label: ticker,
      data: dayLabels.map(day => dailyTickerAverage[day]?.[ticker] ?? null),
      fill: false,
      borderColor: tickerColors[ticker] || 'rgb(153, 102, 255)'
    }));

    avgByDayChart.data.labels = dayLabels;
    avgByDayChart.data.datasets = datasets;
    avgByDayChart.update();

    const tickerLabels = Object.keys(byTicker).sort();
    const tickerValues = tickerLabels.map(t => byTicker[t]);
    avgByTickerChart.data.labels = tickerLabels;
    avgByTickerChart.data.datasets[0].data = tickerValues;
    avgByTickerChart.update();
  }

  async function fetchAndRenderSentimentCounts(startISO, endISO) {
    const params = [];
    if (startISO) params.push(`start_date=${isoToDDMMYYYY(startISO)}`);
    if (endISO) params.push(`end_date=${isoToDDMMYYYY(endISO)}`);
    const url = `/api/sentiment_counts_by_day${params.length ? '?' + params.join('&') : ''}`;
    const resp = await fetch(url);
    const data = await resp.json();
    const countsByDay = data.sentiment_counts_by_day || {};
    const dayLabels = Object.keys(countsByDay).sort((a, b) => {
      const [da, ma, ya] = a.split('-');
      const [db, mb, yb] = b.split('-');
      return new Date(`${ya}-${ma}-${da}`) - new Date(`${yb}-${mb}-${db}`);
    });

    const positiveData = dayLabels.map(d => countsByDay[d]?.POSITIVE || 0);
    const negativeData = dayLabels.map(d => countsByDay[d]?.NEGATIVE || 0);
    const neutralData = dayLabels.map(d => countsByDay[d]?.NEUTRAL || 0);

    sentimentCountChart.data.labels = dayLabels;
    sentimentCountChart.data.datasets = [
      { label: 'Positive', data: positiveData, backgroundColor: 'rgba(75, 192, 192, 0.7)' },
      { label: 'Negative', data: negativeData, backgroundColor: 'rgba(255, 99, 132, 0.7)' },
      { label: 'Neutral', data: neutralData, backgroundColor: 'rgba(201, 203, 207, 0.7)' }
    ];
    sentimentCountChart.update();
  }
});
