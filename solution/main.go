package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	reader := bufio.NewReader(os.Stdin)

	var n, m int
	fmt.Fscan(reader, &n, &m)

	values := make([]int, n)
	for i := 0; i < n; i++ {
		fmt.Fscan(reader, &values[i])
	}

	adj := make([][]int, n)
	for i := 0; i < n; i++ {
		adj[i] = []int{}
	}

	for i := 0; i < m; i++ {
		var a, b int
		fmt.Fscan(reader, &a, &b)
		a--
		b--
		adj[a] = append(adj[a], b)
		adj[b] = append(adj[b], a)
	}

	// dp[mask] = битовая маска возможных последних островов для посещённого множества mask
	dp := make([]int, 1<<n)

	// Начинаем с острова 0 (1 в 1-индексации)
	dp[1] = 1

	for mask := 1; mask < (1 << n); mask++ {
		if dp[mask] == 0 {
			continue
		}
		for last := 0; last < n; last++ {
			if dp[mask]&(1<<last) == 0 {
				continue
			}
			for _, next := range adj[last] {
				if mask&(1<<next) == 0 {
					dp[mask|(1<<next)] |= (1 << next)
				}
			}
		}
	}

	// Находим максимальную сумму среди достижимых масок
	maxSum := values[0] // Минимум — сокровище с острова 1
	for mask := 1; mask < (1 << n); mask++ {
		if dp[mask] != 0 {
			sum := 0
			for i := 0; i < n; i++ {
				if mask&(1<<i) != 0 {
					sum += values[i]
				}
			}
			if sum > maxSum {
				maxSum = sum
			}
		}
	}

	fmt.Println(maxSum)
}
