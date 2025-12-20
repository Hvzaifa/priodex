export class MaxHeap {
    constructor() {
        this.heap = [];  
    }
    
    insert(article, score) {
        this.heap.push({ article, score });
        this._bubbleUp(this.heap.length - 1);  // Maintain heap property
    }
    
    // Get highest priority article
    extractMax() {
        if (this.heap.length === 0) return null;
        if (this.heap.length === 1) return this.heap.pop();
        
        const max = this.heap[0];
        this.heap[0] = this.heap.pop();  // Move last to root
        this._bubbleDown(0);  // Restore heap property
        return max;
    }
    
    // Move element up until heap property satisfied - Heapify
    _bubbleUp(index) {
        while (index > 0) {
            const parentIndex = Math.floor((index - 1) / 2);
            if (this.heap[index].score <= this.heap[parentIndex].score) break;
            
            [this.heap[index], this.heap[parentIndex]] = 
            [this.heap[parentIndex], this.heap[index]];
            index = parentIndex;
        }
    }
    
    // Move element down until heap property satisfied
    _bubbleDown(index) {
        while (true) {
            const leftChild = 2 * index + 1;
            const rightChild = 2 * index + 2;
            let largest = index;
            
            if (leftChild < this.heap.length && 
                this.heap[leftChild].score > this.heap[largest].score) {
                largest = leftChild;
            }
            
            if (rightChild < this.heap.length && 
                this.heap[rightChild].score > this.heap[largest].score) {
                largest = rightChild;
            }
            
            if (largest === index) break;
            
            [this.heap[index], this.heap[largest]] = 
            [this.heap[largest], this.heap[index]];
            index = largest;
        }
    }
    
    // Convert heap to sorted array
    toSortedArray() {
        const sorted = [];
        const tempHeap = [...this.heap];  // Don't destroy original
        
        while (this.heap.length > 0) {
            sorted.push(this.extractMax().article);
        }
        
        this.heap = tempHeap;  // Restore original
        return sorted;
    }
}

