// CoSync - Interactive Collaborative Whiteboard

class CollaborativeWhiteboard {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.drawing = false;
        
        // Default configuration
        this.currentColor = '#ffffff';
        this.currentSize = 5;
        this.lastX = 0;
        this.lastY = 0;
        
        // Hooks for external messaging (WebRTC Data Channel)
        this.onDrawStroke = null; // Callback: (x0, y0, x1, y1, color, size)
        this.onClearBoard = null;  // Callback: ()
        
        this.init();
    }
    
    init() {
        // Event Listeners for Drawing
        this.canvas.addEventListener('mousedown', this.startDrawing.bind(this));
        this.canvas.addEventListener('mousemove', this.draw.bind(this));
        this.canvas.addEventListener('mouseup', this.stopDrawing.bind(this));
        this.canvas.addEventListener('mouseout', this.stopDrawing.bind(this));
        
        // Support Touch Screens
        this.canvas.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.canvas.dispatchEvent(mouseEvent);
        }, { passive: true });
        
        this.canvas.addEventListener('touchmove', (e) => {
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.canvas.dispatchEvent(mouseEvent);
        }, { passive: true });
        
        this.canvas.addEventListener('touchend', () => {
            const mouseEvent = new MouseEvent('mouseup', {});
            this.canvas.dispatchEvent(mouseEvent);
        }, { passive: true });
        
        // UI Controls setup
        this.setupUI();
        
        // Handle Resize
        window.addEventListener('resize', this.resizeCanvas.bind(this));
        setTimeout(() => this.resizeCanvas(), 100);
    }
    
    setupUI() {
        // Color swatches selection
        const swatches = document.querySelectorAll('.color-swatch');
        swatches.forEach(swatch => {
            swatch.addEventListener('click', (e) => {
                swatches.forEach(s => s.classList.remove('active'));
                swatch.classList.add('active');
                this.currentColor = swatch.dataset.color;
            });
        });
        
        // Custom Color Picker
        const customColor = document.getElementById('customColorPicker');
        if (customColor) {
            customColor.addEventListener('input', (e) => {
                swatches.forEach(s => s.classList.remove('active'));
                this.currentColor = e.target.value;
            });
        }
        
        // Pen size select
        const sizeSelect = document.getElementById('penSize');
        if (sizeSelect) {
            sizeSelect.addEventListener('change', (e) => {
                this.currentSize = parseInt(e.target.value);
            });
        }
        
        // Clear board button
        const clearBtn = document.getElementById('btnClearBoard');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearLocal();
                if (this.onClearBoard) {
                    this.onClearBoard();
                }
            });
        }
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // To prevent losing drawing, we save the current canvas content
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.canvas.width;
        tempCanvas.height = this.canvas.height;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(this.canvas, 0, 0);
        
        // Set new size based on viewport
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        
        // Redraw previous content
        this.ctx.drawImage(tempCanvas, 0, 0, rect.width, rect.height);
        
        // Restore canvas drawing line defaults
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
    }
    
    startDrawing(e) {
        this.drawing = true;
        const coords = this.getCoords(e);
        this.lastX = coords.x;
        this.lastY = coords.y;
    }
    
    draw(e) {
        if (!this.drawing) return;
        
        const coords = this.getCoords(e);
        const currentX = coords.x;
        const currentY = coords.y;
        
        // Draw locally
        this.ctx.beginPath();
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(currentX, currentY);
        this.ctx.strokeStyle = this.currentColor;
        this.ctx.lineWidth = this.currentSize;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.stroke();
        
        // Send stroke coordinates relative (normalized 0 to 1) so it syncs perfectly on different screen sizes
        if (this.onDrawStroke) {
            const relX0 = this.lastX / this.canvas.width;
            const relY0 = this.lastY / this.canvas.height;
            const relX1 = currentX / this.canvas.width;
            const relY1 = currentY / this.canvas.height;
            
            this.onDrawStroke(relX0, relY0, relX1, relY1, this.currentColor, this.currentSize);
        }
        
        this.lastX = currentX;
        this.lastY = currentY;
    }
    
    stopDrawing() {
        this.drawing = false;
    }
    
    getCoords(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }
    
    // API for drawing strokes received from remote users
    drawRemoteStroke(relX0, relY0, relX1, relY1, color, size) {
        const x0 = relX0 * this.canvas.width;
        const y0 = relY0 * this.canvas.height;
        const x1 = relX1 * this.canvas.width;
        const y1 = relY1 * this.canvas.height;
        
        this.ctx.beginPath();
        this.ctx.moveTo(x0, y0);
        this.ctx.lineTo(x1, y1);
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = size;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.stroke();
    }
    
    // Clear canvas locally
    clearLocal() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}
