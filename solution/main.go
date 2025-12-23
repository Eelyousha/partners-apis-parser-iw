package main

import (
	"bufio"
	"container/heap"
	"fmt"
	"os"
)

type Item struct {
	time int
	row  int
	col  int
}

type PriorityQueue []Item

func (pq PriorityQueue) Len() int           { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool { return pq[i].time < pq[j].time }
func (pq PriorityQueue) Swap(i, j int)      { pq[i], pq[j] = pq[j], pq[i] }
func (pq *PriorityQueue) Push(x any)        { *pq = append(*pq, x.(Item)) }
func (pq *PriorityQueue) Pop() any {
	old := *pq
	n := len(old)
	x := old[n-1]
	*pq = old[0 : n-1]
	return x
}

func main() {
	reader := bufio.NewReader(os.Stdin)
	writer := bufio.NewWriter(os.Stdout)
	defer writer.Flush()

	var n, m int
	fmt.Fscan(reader, &n, &m)

	h := make([][]int, n)
	result := make([][]int, n)
	for i := 0; i < n; i++ {
		h[i] = make([]int, m)
		result[i] = make([]int, m)
		for j := 0; j < m; j++ {
			fmt.Fscan(reader, &h[i][j])
			result[i][j] = -1
		}
	}

	pq := &PriorityQueue{}
	heap.Init(pq)

	// Добавляем все водные клетки (h=0) с временем 0
	for i := 0; i < n; i++ {
		for j := 0; j < m; j++ {
			if h[i][j] == 0 {
				heap.Push(pq, Item{0, i, j})
			}
		}
	}

	// Добавляем граничные клетки — они соседствуют с океаном снаружи карты
	// Граничная клетка затопляется когда уровень воды достигает её высоты
	for i := 0; i < n; i++ {
		if h[i][0] > 0 {
			heap.Push(pq, Item{h[i][0], i, 0})
		}
		if m > 1 && h[i][m-1] > 0 {
			heap.Push(pq, Item{h[i][m-1], i, m - 1})
		}
	}
	for j := 1; j < m-1; j++ {
		if h[0][j] > 0 {
			heap.Push(pq, Item{h[0][j], 0, j})
		}
		if n > 1 && h[n-1][j] > 0 {
			heap.Push(pq, Item{h[n-1][j], n - 1, j})
		}
	}

	dx := []int{-1, 1, 0, 0}
	dy := []int{0, 0, -1, 1}

	// Dijkstra от всех источников воды
	for pq.Len() > 0 {
		item := heap.Pop(pq).(Item)
		t, r, c := item.time, item.row, item.col

		if result[r][c] != -1 {
			continue // уже обработано
		}
		result[r][c] = t

		for d := 0; d < 4; d++ {
			nr, nc := r+dx[d], c+dy[d]
			if nr >= 0 && nr < n && nc >= 0 && nc < m && result[nr][nc] == -1 {
				// Время затопления соседа = max(текущее время, высота соседа)
				newTime := t
				if h[nr][nc] > newTime {
					newTime = h[nr][nc]
				}
				heap.Push(pq, Item{newTime, nr, nc})
			}
		}
	}

	// Вывод результата
	for i := 0; i < n; i++ {
		for j := 0; j < m; j++ {
			if j > 0 {
				fmt.Fprint(writer, " ")
			}
			fmt.Fprint(writer, result[i][j])
		}
		fmt.Fprintln(writer)
	}
}
