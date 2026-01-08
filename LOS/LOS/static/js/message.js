class Modal {
    constructor() {
        this.config = {
            apiUrl: '/message/receive',
        }
        this.modalMask = document.getElementById('modalMask');
        this.modalContent = document.getElementById('modalContent');
    }

    /**
     * 打开模态框并填充内容
     * @param {Object} data - 消息数据，包含 title、time、content 属性
     */
    open(data) {
        if (!this.modalMask || !this.modalContent) {
            console.error('模态框元素未找到');
            return;
        }

        // 填充模态框内容
        this.modalContent.innerHTML = `
            <div class="message-detail">
                <div class="message-id">消息ID：${data.title || ''}</div>
                <div class="message-time">发送时间：${data.time || ''}</div>
                <div class="message-content">
                    <strong>消息内容：</strong>
                    <p>${data.content || ''}</p>
                </div>
            </div>
        `;

        // 显示模态框
        this.modalMask.style.display = 'flex';
        this.modalMask.style.zIndex = '1000';
    }

    /**
     * 关闭模态框
     */
    close() {
        if (this.modalMask) {
            this.modalMask.style.display = 'none';
        }
    }

    /**
     * 初始化事件监听
     */
    init() {
        // 点击模态框外部关闭模态框
        this.modalMask?.addEventListener('click', (e) => {
            if (e.target === this.modalMask) {
                this.close();
            }
        });
    }
}

// 创建全局模态框实例
const modal = new Modal();

// 初始化模态框
document.addEventListener('DOMContentLoaded', () => {
    modal.init();
});

// 全局函数：打开模态框
function modalOpen(data) {
    modal.open(data);
}

// 全局函数：关闭模态框
function modalClose() {
    modal.close();
}