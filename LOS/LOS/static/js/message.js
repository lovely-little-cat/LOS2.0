class Modal {
    constructor() {
        this.config = {
            apiUrl: '/message/receive',
        }
        this.modalMask = document.getElementById('modalMask');
        this.modalContent = document.getElementById('modalContent');
    }

  
    open(data) {
        if (!this.modalMask || !this.modalContent) {
            console.error('模态框元素未找到');
            return;
        }


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


        this.modalMask.style.display = 'flex';
        this.modalMask.style.zIndex = '1000';
    }


    close() {
        if (this.modalMask) {
            this.modalMask.style.display = 'none';
        }
    }


    init() {

        this.modalMask?.addEventListener('click', (e) => {
            if (e.target === this.modalMask) {
                this.close();
            }
        });
    }
}


const modal = new Modal();


document.addEventListener('DOMContentLoaded', () => {
    modal.init();
});


function modalOpen(data) {
    modal.open(data);
}


function modalClose() {
    modal.close();
}