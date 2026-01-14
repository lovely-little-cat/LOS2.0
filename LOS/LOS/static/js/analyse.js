/**
 * 利润图表管理器 - 具备完整生命周期：初始化 → 挂载 → 更新 → 销毁
 */
class ProfitChartManager {
  // ===== 1. 初始化生命周期=====
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
        sell: 'sellChart' // 新增销售量图表ID
      },
      buttonIds: {
        refreshAll: 'refreshBtn',
        refreshWeek: 'refreshWeekBtn',
        refreshMonth: 'refreshMonthBtn',
        refreshYear: 'refreshYearBtn',
        refreshStock: 'refreshStockBtn',
        refreshSell: 'refreshSellBtn' // 新增销售量刷新按钮ID
      }
    };

    // 状态管理：存储图表实例、事件监听函数（用于销毁时解绑）
    this.state = {
      chartInstances: {
        weekly: null,
        oneMonth: null,
        twelveMonths: null,
        stockSell: null,
        sell: null // 新增销售量图表实例
      },
      eventHandlers: {}
    };

    // 初始化阶段：绑定生命周期钩子（可选，用于扩展）
    this.beforeInit = () => {};
    this.afterInit = () => {};
    this.beforeDestroy = () => {};
    this.afterDestroy = () => {};
  }

  // ===== 2. 核心初始化方法（入口）=====
  init() {
    this.beforeInit();
    console.log('ProfitChartManager 初始化中...');

    // 校验DOM元素是否存在
    this._validateDOM();
    // 绑定按钮事件
    this._bindEvents();
    // 挂载图表（首次渲染）
    this.mount();

    this.afterInit();
    console.log('ProfitChartManager 初始化完成');
  }

  // ===== 3. 挂载生命周期（首次渲染图表）=====
  async mount() {
    console.log('图表挂载中...');
    // 并行渲染所有图表，提升性能
    await Promise.all([
      this._renderWeeklyChart(),
      this._renderOneMonthChart(),
      this._renderTwelveMonthsChart(),
      this._renderStockSellChart(),
      this._renderSellChart() // 新增销售量图表渲染
    ]);
    console.log('图表挂载完成');
  }

  // ===== 4. 更新生命周期（刷新指定/所有图表）=====
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
        alert('库存数据已刷新！');
        break;
      case 'sell': // 新增销售量更新逻辑
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

  // ===== 5. 销毁生命周期（清理资源）=====
  destroy() {
    this.beforeDestroy();
    console.log('ProfitChartManager 销毁中...');

    // 销毁所有图表实例
    Object.values(this.state.chartInstances).forEach(instance => {
      if (instance) instance.destroy();
    });
    // 解绑所有事件
    Object.entries(this.state.eventHandlers).forEach(([id, handler]) => {
      const el = document.getElementById(id);
      el?.removeEventListener('click', handler);
    });
    // 清空状态
    this.state = { chartInstances: {}, eventHandlers: {} };

    this.afterDestroy();
    console.log('ProfitChartManager 销毁完成');
  }

  // ===== 私有辅助方法：校验DOM元素 =====
  _validateDOM() {
    // 校验图表容器
    Object.values(this.config.chartIds).forEach(id => {
      if (!document.getElementById(id)) {
        throw new Error(`图表容器不存在：#${id}`);
      }
    });
    // 校验按钮（非必选，仅警告）
    Object.values(this.config.buttonIds).forEach(id => {
      if (!document.getElementById(id)) {
        console.warn(`刷新按钮不存在：#${id}（部分刷新功能可能失效）`);
      }
    });
  }

  // ===== 私有辅助方法：绑定按钮事件 =====
  _bindEvents() {
    const { buttonIds } = this.config;

    // 绑定「刷新所有」按钮
    this.state.eventHandlers[buttonIds.refreshAll] = () => this.update('all');
    document.getElementById(buttonIds.refreshAll)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshAll]
    );

    // 绑定「近7天」刷新按钮
    this.state.eventHandlers[buttonIds.refreshWeek] = () => this.update('weekly');
    document.getElementById(buttonIds.refreshWeek)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshWeek]
    );

    // 绑定「近30天」刷新按钮
    this.state.eventHandlers[buttonIds.refreshMonth] = () => this.update('oneMonth');
    document.getElementById(buttonIds.refreshMonth)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshMonth]
    );

    // 绑定「近12个月」刷新按钮
    this.state.eventHandlers[buttonIds.refreshYear] = () => this.update('twelveMonths');
    document.getElementById(buttonIds.refreshYear)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshYear]
    );

    // 绑定「库存」刷新按钮
    this.state.eventHandlers[buttonIds.refreshStock] = () => this.update('stockSell');
    document.getElementById(buttonIds.refreshStock)?.addEventListener(
      'click',
      this.state.eventHandlers[buttonIds.refreshStock]
    );

    // 新增：绑定「销售量」刷新按钮
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
      return result.data || result; // 适配stock_sell接口返回的完整数据
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

    // 销毁旧实例
    if (this.state.chartInstances.weekly) {
      this.state.chartInstances.weekly.destroy();
    }

    // 渲染新图表（月-日格式，每日利润）
    this.state.chartInstances.weekly = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(item => item.time_key), // 月-日
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
        labels: data.map(item => item.time_key), // 月-日
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
          x: { title: { display: true, text: '日期（月-日）' } }
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
        labels: data.map(item => item.time_key), // 年-月
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

  // ===== 私有辅助方法：渲染库存分析图表（适配推荐算法） =====
  async _renderStockSellChart() {
    const result = await this._fetchData(this.config.apiUrls.stockSell);
    const ctx = document.getElementById(this.config.chartIds.stockSell).getContext('2d');
    const sortedData = result.sorted_price || [];
    const warnThreshold = result.warn_threshold || 20;

    if (this.state.chartInstances.stockSell) {
      this.state.chartInstances.stockSell.destroy();
    }

    // 提取数据：商品ID、库存、补货优先级
    const labels = sortedData.map(item => `商品${item.products_id}`);
    const stockData = sortedData.map(item => item.stock || 0);
    const priorityData = sortedData.map(item => item.recommend_priority || 0);
    // 标记需要补货的商品（库存<=20）
    const backgroundColor = sortedData.map(item => 
      item.need_restock ? 'rgba(255, 99, 132, 0.6)' : 'rgba(54, 162, 235, 0.6)'
    );

    this.state.chartInstances.stockSell = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: '库存量',
            data: stockData,
            backgroundColor: backgroundColor,
            borderColor: item => item.need_restock ? 'rgba(255, 99, 132, 1)' : 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            yAxisID: 'y'
          },
          {
            label: '补货优先级',
            data: priorityData,
            type: 'line',
            backgroundColor: 'rgba(255, 206, 86, 0.2)',
            borderColor: 'rgba(255, 206, 86, 1)',
            borderWidth: 2,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: '库存量' },
            // 新增预警线（库存20）
            plugins: {
              annotation: {
                annotations: {
                  line1: {
                    type: 'line',
                    yMin: warnThreshold,
                    yMax: warnThreshold,
                    borderColor: 'rgb(255, 99, 132)',
                    borderWidth: 2,
                    label: { display: true, content: '库存预警线(20)' }
                  }
                }
              }
            }
          },
          y1: {
            beginAtZero: true,
            position: 'right',
            title: { display: true, text: '补货优先级' },
            grid: { drawOnChartArea: false }
          },
          x: { title: { display: true, text: '商品ID' } }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const item = sortedData[ctx.dataIndex];
                return [
                  `库存量：${item.stock}`,
                  `出售量：${item.sell}`,
                  `补货优先级：${item.recommend_priority}`,
                  item.need_restock ? '⚠️ 需要补货' : '✅ 库存充足'
                ];
              }
            }
          },
          legend: { position: 'top' }
        }
      }
    });
  }

  // ===== 新增：渲染销售量分析图表（按出售量排序） =====
  async _renderSellChart() {
    const result = await this._fetchData(this.config.apiUrls.stockSell);
    const ctx = document.getElementById(this.config.chartIds.sell).getContext('2d');
    const sortedData = result.sorted_price || [];

    if (this.state.chartInstances.sell) {
      this.state.chartInstances.sell.destroy();
    }

    // 提取数据：商品ID、出售量、利润（售价-成本）
    const labels = sortedData.map(item => `商品${item.products_id}`);
    const sellData = sortedData.map(item => item.sell || 0);
    const profitPerUnit = sortedData.map(item => (item.products_price - item.cost) || 0);

    this.state.chartInstances.sell = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: '出售量',
            data: sellData,
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            yAxisID: 'y'
          },
          {
            label: '单位利润（元）',
            data: profitPerUnit,
            type: 'line',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 2,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: '出售量' },
          },
          y1: {
            beginAtZero: true,
            position: 'right',
            title: { display: true, text: '单位利润（元）' },
            grid: { drawOnChartArea: false }
          },
          x: { title: { display: true, text: '商品ID（按出售量降序）' } }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const item = sortedData[ctx.dataIndex];
                return [
                  `出售量：${item.sell}`,
                  `单位利润：${(item.products_price - item.cost).toFixed(2)} 元`,
                  `总利润：${(item.sell * (item.products_price - item.cost)).toFixed(2)} 元`
                ];
              }
            }
          }
        }
      }
    });
  }
}

// 初始化图表管理器
document.addEventListener('DOMContentLoaded', () => {
  const chartManager = new ProfitChartManager();
  chartManager.init();

  // 暴露全局刷新函数（适配HTML中的onclick）
  window.refreshWeeklyChart = () => chartManager.update('weekly');
  window.refreshOneMonthChart = () => chartManager.update('oneMonth');
  window.refreshMonthlyChart = () => chartManager.update('twelveMonths');
  window.refreshStockChart = () => chartManager.update('stockSell');
  window.refreshSellChart = () => chartManager.update('sell');
});