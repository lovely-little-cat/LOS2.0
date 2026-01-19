class ProfitChartManager {
  // ===== 初始化生命周期=====
  constructor() {
    this.config = {
      apiUrls: {
        weekly: '/analyse/weekly',
        oneMonth: '/analyse/onemonth',
        twelveMonths: '/analyse/monthly',
        stockSell: '/analyse/stock_sell',
      },
      chartIds: {
        weekly: 'weeklyChart',
        oneMonth: 'oneMonthChart',
        twelveMonths: 'monthlyChart',
        stockSell: 'stockChart',
        sell: 'sellChart' 
      },
      buttonIds: {
        refreshAll: 'refreshBtn',
        refreshWeek: 'refreshWeekBtn',
        refreshMonth: 'refreshMonthBtn',
        refreshYear: 'refreshYearBtn',
        refreshStock: 'refreshStockBtn',
        refreshSell: 'refreshSellBtn' 
      }
    };

    // 状态管理：存储图表实例、事件监听函数
    this.state = {
      chartInstances: {
        weekly: null,
        oneMonth: null,
        twelveMonths: null,
        stockSell: null,
        sell: null 
      },
      eventHandlers: {}
    };

    // 初始化阶段：绑定生命周期钩子
    this.beforeInit = () => {};
    this.afterInit = () => {};
    this.beforeDestroy = () => {};
    this.afterDestroy = () => {};
  }

  // ===== 2. 核心初始化方法=====
  init() {
    this.beforeInit();
    console.log('ProfitChartManager 初始化中...');

    this._validateDOM();
    this._bindEvents();
    this.mount();

    this.afterInit();
    console.log('ProfitChartManager 初始化完成');
  }

  // ===== 3. 挂载生命周期=====
  async mount() {
    console.log('图表挂载中...');
    await Promise.all([
      this._renderWeeklyChart(),
      this._renderOneMonthChart(),
      this._renderTwelveMonthsChart(),
      this._renderStockSellChart(),
      this._renderSellChart()
    ]);
    await this._renderRestockReminder();
    console.log('图表挂载完成');
  }

  // ===== 4. 更新生命周期=====
  async update(type = 'all') {
    console.log(`更新${type === 'all' ? '所有' : type}图表...`);
    switch (type) {
      case 'weekly':
        await this._renderWeeklyChart();
        alert('近7天图表已刷新！');
        break;
      case 'oneMonth':
        await this._renderOneMonthChart();
        alert('近30天图表已刷新！');
        break;
      case 'twelveMonths':
        await this._renderTwelveMonthsChart();
        alert('近12个月图表已刷新！');
        break;
      case 'stockSell':
        await this._renderStockSellChart();
        await this._renderRestockReminder(); 
        alert('库存数据已刷新！');
        break;
      case 'sell': 
        await this._renderSellChart();
        alert('销售量数据已刷新！');
        break;
      case 'all':
        await this.mount();
        alert('所有图表数据已刷新！');
        break;
      default:
        console.warn('未知的更新类型：', type);
    }
  }

  // ===== 5. 销毁生命周期=====
  destroy() {
    this.beforeDestroy();
    console.log('ProfitChartManager 销毁中...');

    Object.values(this.state.chartInstances).forEach(instance => {
      if (instance) instance.destroy();
    });
  
    Object.entries(this.state.eventHandlers).forEach(([id, handler]) => {
      const el = document.getElementById(id);
      el?.removeEventListener('click', handler);
    });
   
    this.state = { chartInstances: {}, eventHandlers: {} };
    this.afterDestroy();
    console.log('ProfitChartManager 销毁完成');
  }

  // ===== 私有辅助方法：校验DOM元素 =====
  _validateDOM() {
    Object.values(this.config.chartIds).forEach(id => {
      if (!document.getElementById(id)) {
        throw new Error(`图表容器不存在：#${id}`);
      }
    });
    Object.values(this.config.buttonIds).forEach(id => {
      if (!document.getElementById(id)) {
        console.warn(`刷新按钮不存在：#${id}（部分刷新功能可能失效）`);
      }
    });

    if (!document.getElementById('restockReminder')) {
      console.warn('补货提醒容器不存在：#restockReminder');
    }
  }

  // ===== 私有辅助方法：绑定按钮事件 =====
  _bindEvents() {
    const { buttonIds } = this.config;

    this.state.eventHandlers[buttonIds.refreshAll] = () => this.update('all');
    document.getElementById(buttonIds.refreshAll)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshAll]
    );

    this.state.eventHandlers[buttonIds.refreshWeek] = () => this.update('weekly');
    document.getElementById(buttonIds.refreshWeek)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshWeek]
    );

    this.state.eventHandlers[buttonIds.refreshMonth] = () => this.update('oneMonth');
    document.getElementById(buttonIds.refreshMonth)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshMonth]
    );

    this.state.eventHandlers[buttonIds.refreshYear] = () => this.update('twelveMonths');
    document.getElementById(buttonIds.refreshYear)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshYear]
    );

    this.state.eventHandlers[buttonIds.refreshStock] = () => this.update('stockSell');
    document.getElementById(buttonIds.refreshStock)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshStock]
    );

    this.state.eventHandlers[buttonIds.refreshSell] = () => this.update('sell');
    document.getElementById(buttonIds.refreshSell)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshSell]
    );
  }

  // ===== 私有辅助方法：请求数据 =====
  async _fetchData(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`请求失败（状态码：${response.status}）`);
      }
      const result = await response.json();
      if (result.status === 'error') throw new Error(result.error);
      return result.data || result; 
    } catch (error) {
      console.error('数据请求失败：', error);
      alert(`获取数据失败：${error.message}`);
      return {};
    }
  }

  // ===== 私有辅助方法：渲染近7天图表 =====
  async _renderWeeklyChart() {
    const data = await this._fetchData(this.config.apiUrls.weekly);
    const ctx = document.getElementById(this.config.chartIds.weekly).getContext('2d');

    if (this.state.chartInstances.weekly) {
      this.state.chartInstances.weekly.destroy();
    }

    this.state.chartInstances.weekly = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(item => item.time_key),
        datasets: [{
          label: '每日利润（元）',
          data: data.map(item => item.profit || 0),
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 2,
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, title: { display: true, text: '利润（元）' } },
          x: { title: { display: true, text: '日期（月-日）' } }
        },
        plugins: {
          tooltip: { callbacks: { label: (ctx) => `利润：${ctx.raw.toFixed(2)} 元` } }
        }
      }
    });
  }

  // ===== 私有辅助方法：渲染近30天图表 =====
  async _renderOneMonthChart() {
    const data = await this._fetchData(this.config.apiUrls.oneMonth);
    const ctx = document.getElementById(this.config.chartIds.oneMonth).getContext('2d');

    if (this.state.chartInstances.oneMonth) {
      this.state.chartInstances.oneMonth.destroy();
    }

    this.state.chartInstances.oneMonth = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(item => item.time_key), 
        datasets: [{
          label: '每日利润（元）',
          data: data.map(item => item.profit || 0),
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 2,
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, title: { display: true, text: '利润（元）' } },
          x: { title: { display: true, text: '日期（年-月-日）' } }
        },
        plugins: {
          tooltip: { callbacks: { label: (ctx) => `利润：${ctx.raw.toFixed(2)} 元` } }
        }
      }
    });
  }

  // ===== 私有辅助方法：渲染近12个月图表 =====
  async _renderTwelveMonthsChart() {
    const data = await this._fetchData(this.config.apiUrls.twelveMonths);
    const ctx = document.getElementById(this.config.chartIds.twelveMonths).getContext('2d');

    if (this.state.chartInstances.twelveMonths) {
      this.state.chartInstances.twelveMonths.destroy();
    }

    this.state.chartInstances.twelveMonths = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(item => item.time_key), 
        datasets: [{
          label: '每月利润（元）',
          data: data.map(item => item.profit || 0),
          backgroundColor: 'rgba(153, 102, 255, 0.5)',
          borderColor: 'rgba(153, 102, 255, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, title: { display: true, text: '利润（元）' } },
          x: { title: { display: true, text: '日期（年-月）' } }
        },
        plugins: {
          tooltip: { callbacks: { label: (ctx) => `利润：${ctx.raw.toFixed(2)} 元` } }
        }
      }
    });
  }

  // ===== 私有辅助方法：渲染库存分析图表 =====
  async _renderStockSellChart() {
    const result = await this._fetchData(this.config.apiUrls.stockSell);
    const ctx = document.getElementById(this.config.chartIds.stockSell).getContext('2d');
    const sortedByStock = result.sorted_by_stock || [];
    const warnThreshold = result.min_stock || 20;

    if (this.state.chartInstances.stockSell) {
      this.state.chartInstances.stockSell.destroy();
    }

    const labels = sortedByStock.map(item => `商品${item.products_id}`);
    //test
    const stockData = sortedByStock.map(item => item.stock || 100);
    const backgroundColors = stockData.map(stock => 
      stock <= warnThreshold ? 'rgba(255, 99, 132, 0.5)' : 'rgba(75, 192, 192, 0.5)'
    );

    this.state.chartInstances.stockSell = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: '库存量',
          data: stockData,
          backgroundColor: backgroundColors,
          borderColor: stockData.map(stock => 
            stock <= warnThreshold ? 'rgba(255, 99, 132, 1)' : 'rgba(75, 192, 192, 1)'
          ),
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { 
            beginAtZero: true, 
            title: { display: true, text: '库存量' },
            annotations: {
              line: {
                value: warnThreshold,
                borderColor: 'red',
                borderWidth: 5,
                label: {
                  display: true,
                  content: '库存预警阈值',
                  position: 'end'
                }
              }
            }
          },
          x: { title: { display: true, text: '商品ID' } }
        },
        plugins: {
          tooltip: { 
            callbacks: { 
              label: (ctx) => {
                const stock = ctx.raw;
                const tip = `库存量：${stock}${stock <= warnThreshold ? '（需补货）' : ''}`;
                return tip;
              } 
            } 
          }
        }
      }
    });
  }

  // ===== 私有辅助方法：渲染销售量分析图表 =====
  async _renderSellChart() {
    const result = await this._fetchData(this.config.apiUrls.stockSell);
    const ctx = document.getElementById(this.config.chartIds.sell).getContext('2d');
    const sortedBySell = result.sorted_by_sell || [];

    if (this.state.chartInstances.sell) {
      this.state.chartInstances.sell.destroy();
    }

   
    const labels = sortedBySell.map(item => `商品${item.products_id}`);
    const sellData = sortedBySell.map(item => item.sell || 0);

    this.state.chartInstances.sell = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: '销售量',
          data: sellData,
          backgroundColor: 'rgba(255, 159, 64, 0.5)',
          borderColor: 'rgba(255, 159, 64, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, title: { display: true, text: '销售量' } },
          x: { title: { display: true, text: '商品ID' } }
        },
        plugins: {
          tooltip: { 
            callbacks: { 
              label: (ctx) => `销售量：${ctx.raw}` 
            } 
          }
        }
      }
    });
  }

  // ===== 私有辅助方法：渲染补货提醒列表 =====
  async _renderRestockReminder() {
    const result = await this._fetchData(this.config.apiUrls.stockSell);
    const restockList = result.restock_list || [];
    const container = document.getElementById('restockReminder');
    
    if (!container) return;

    if (restockList.length === 0) {
      container.innerHTML = `
        <div class="restock-empty">
          <i class="fa-solid fa-check-circle"></i>
          <span>暂无需要补货的商品</span>
        </div>
      `;
      return;
    }

    let html = `
      <div class="restock-header">
        <h3><i class="fa-solid fa-triangle-exclamation"></i> 补货推荐</h3>
      </div>
      <table class="restock-table">
        <thead>
          <tr>
            <th>商品ID</th>
            <th>当前库存</th>
            <th>销售量</th>
            <th>补货优先级</th>
          </tr>
        </thead>
        <tbody>
    `;
    restockList.forEach(item => {
      html += `
        <tr>
          <td>商品${item.products_id}</td>
          <td class="stock-warning">${item.current_stock}</td>
          <td>${item.sell_volume}</td>
          <td>${item.priority}</td>
        </tr>
      `;
    });
    html += `
        </tbody>
      </table>
    `;
    container.innerHTML = html;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const chartManager = new ProfitChartManager();
  chartManager.init();
});