package sample

import "testing"

func TestWorks(t *testing.T) {
	if true != true {
		t.Fail()
	}
}
