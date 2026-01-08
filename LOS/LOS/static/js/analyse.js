// 定义内部常量，避免依赖全局变量
const CHART_TYPES = {
  BAR: 'bar',
  LINE: 'line'
};
const TIME_TYPES = {
  DAY: 'day',
  MONTH: 'month'
};

class AnalyseChart {
  constructor() {
    this.chartsConfig = [
      {
        id: 'weeklyChart',
        api: '/analyse/weekly',
        type: CHART_TYPES.BAR,
        timeType: TIME_TYPES.DAY,
        count: 7,
        color: 'rgba(75, 192, 192, 1)'
      },
      {
        id: 'oneMonthChart',
        api: '/analyse/onemonth',
        type: CHART_TYPES.LINE,
        timeType: TIME_TYPES.DAY,
        count: 30,
        color: 'rgba(54, 162, 235, 1)'
      },
      {
        id: 'twelveMonthsChart',
        api: '/analyse/monthly',
        type: CHART_TYPES.LINE,
        timeType: TIME_TYPES.MONTH,
        count: 12,
        color: 'rgba(255, 99, 132, 1)'
      }
    ];
    this.chartInstances = {};
    this.eventCallbacks = {
      timeRangeChange: () => this.update()
    };
  }

  init() {
    this.bindEvents();
    this.run(); 
  }


  async loadData(config) {
    const fetchOptions = {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      cache: 'no-store'
    };
    try {
      const response = await Promise.race([
        fetch(config.api, fetchOptions),
        new Promise((_, reject) => setTimeout(() => reject(new Error('请求超时')), 10000))
      ]);
      if (!response.ok) throw new Error(`HTTP错误：${response.status} ${response.statusText}`);
      const data = await response.json();
      if (data.status === 'error') throw new Error(data.error);
      return data.data || [];
    } catch (e) {
      this.handleError(config.id, e.message);
      throw e;
    }
  }

  processData(config, sourceData) {
    const labels = this.generateDateLabels(config.timeType, config.count);
    const dataMap = new Map(sourceData.map(item => [item.time_key, Number(item.profit) || 0]));
    return { labels, processedData: labels.map(label => dataMap.get(label) || 0) };
  }

  // 优化：复用实例更新数据，而非销毁重建
  render(config, labels, data) {
    const ctx = document.getElementById(config.id);
    if (!ctx) {
      this.handleError(config.id, `容器 ${config.id} 不存在`);
      return;
    }

    const isLineChart = config.type === CHART_TYPES.LINE;
    const dataset = {
      label: '收益（元）',
      data: data,
      backgroundColor: isLineChart ? 'transparent' : `${config.color}40`,
      borderColor: config.color,
      borderWidth: 2,
      pointRadius: isLineChart ? 4 : 0
    };

    // 若实例存在则更新数据，否则创建新实例
    if (this.chartInstances[config.id]) {
      const instance = this.chartInstances[config.id];
      instance.data.labels = labels;
      instance.data.datasets[0] = dataset;
      instance.update(); // 调用Chart的update方法，性能更优
    } else {
      this.chartInstances[config.id] = new Chart(ctx, {
        type: config.type,
        data: { labels, datasets: [dataset] },
        options: this.getChartOptions(config)
      });
    }
  }

  // 提取通用图表配置，减少重复
  getChartOptions(config) {
    return {
      responsive: true,
      scales: {
        x: { title: { display: true, text: config.timeType === TIME_TYPES.DAY ? '日期' : '月份' } },
        y: { title: { display: true, text: '收益（元）' }, beginAtZero: true }
      },
      plugins: {
        tooltip: { callbacks: { label: (ctx) => `收益：${ctx.raw.toFixed(2)}元` } }
      }
    };
  }

  async run() {
    const tasks = this.chartsConfig.map(async (config) => {
      try {
        const sourceData = await this.loadData(config);
        const { labels, processedData } = this.processData(config, sourceData);
        this.render(config, labels, processedData);
      } catch (e) {
        console.error(`图表 ${config.id} 处理失败：${e.message}`);
      }
    });
    await Promise.all(tasks);
  }

 
  async update() {
    await this.run();
  }

  destroy() {
    Object.values(this.chartInstances).forEach(instance => instance.destroy?.());
    this.chartInstances = {};
    this.unbindEvents();
  }

  generateDateLabels(type, count) {
    const labels = [];
    const today = new Date();
    for (let i = count - 1; i >= 0; i--) {
      const date = new Date(today);
      if (type === TIME_TYPES.DAY) {
        date.setDate(today.getDate() - i);
        labels.push(date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }));
      } else if (type === TIME_TYPES.MONTH) {
        date.setMonth(today.getMonth() - i);
        labels.push(date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit' }));
      }
    }
    return labels;
  }

  
  handleError(containerId, message) {
    const container = document.getElementById(containerId)?.parentNode;
    if (!container) return;
 
    if (this.chartInstances[containerId]) {
      this.chartInstances[containerId].destroy();
      delete this.chartInstances[containerId];
    }
    container.innerHTML = `
      <div class="error-card">
        <p>数据加载失败</p>
        <p>${message}</p>
        <button class="retry-btn" data-target="${containerId}">重试</button>
      </div>
    `;
  }

  bindEvents() {
    const timeRangeSelect = document.getElementById('timeRangeSelect');
    if (timeRangeSelect) {
      timeRangeSelect.addEventListener('change', this.eventCallbacks.timeRangeChange);
    }
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('retry-btn')) {
        this.update();
      }
    });
  }

  unbindEvents() {
    const timeRangeSelect = document.getElementById('timeRangeSelect');
    if (timeRangeSelect) {
      timeRangeSelect.removeEventListener('change', this.eventCallbacks.timeRangeChange);
    }
  }
}