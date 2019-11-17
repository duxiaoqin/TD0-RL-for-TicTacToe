# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 14:49:32 2018

@author: duxiaoqin
Functions:
    (1) On-Policy TD(0) for TicTacToe, epsilon-greedy control
"""

from graphics import *
from tictactoe import *
from tttdraw import *
from tttinput import *
import sys
import time
import math
from random import *
import pickle

def TD0(root, V, alpha, epsilon, learning_time):
    def RandomMove(node):
        moves = node.getAllMoves()
        return moves[randint(0, len(moves)-1)]
    
    def UpdateTerminalNode(node, result):
        key = node.ToString()
        if V.get(key) != None:
            return
        if result == TicTacToe.BLACKWIN:
            V[key] = 1
        elif result == TicTacToe.WHITEWIN:
            V[key] = 0
        else:
            V[key] = 0.5
            
    def UpdateValueFunction(node1, node2, alpha):
        key1 = node1.ToString()
        key2 = node2.ToString()
        if V.get(key1) == None:
            V[key1] = 0.5
        if V.get(key2) == None:
            V[key2] = 0.5
        V[key1] += alpha * (V[key2] - V[key1])
        
    def BestMove(node):
        if node.getPlayer() == TicTacToe.BLACK:
            best_value = -sys.maxsize
            best_move = ()
            moves = node.getAllMoves()
            for move in moves:
                tmp_node = node.clone()
                tmp_node.play(*move)
                key = tmp_node.ToString()
                if V.get(key) == None:
                    continue
                if best_value < V[key]:
                    best_value = V[key]
                    best_move = move
            if best_move == () and len(moves) != 0:
                best_move = RandomMove(node)
            return best_move
        else:
            best_value = sys.maxsize
            best_move = ()
            moves = node.getAllMoves()
            for move in moves:
                tmp_node = node.clone()
                tmp_node.play(*move)
                key = tmp_node.ToString()
                if V.get(key) == None:
                    continue
                if best_value > V[key]:
                    best_value = V[key]
                    best_move = move
            if best_move == () and len(moves) != 0:
                best_move = RandomMove(node)
            return best_move
        
    for i in range(learning_time):
        node = root.clone()
        parent = None
        result = node.isGameOver()
        while result == None:
            if random() < epsilon:
                move = RandomMove(node)
                node.play(*move)
                result = node.isGameOver()
                if result != None:
                    UpdateTerminalNode(node, result)
                    if parent != None:
                        UpdateValueFunction(parent, node, alpha)
                    parent = None
                else:
                    parent = node.clone()
            else:
                move = BestMove(node)
                node.play(*move)
                result = node.isGameOver()
                if result != None:
                    UpdateTerminalNode(node, result)
                if parent != None:
                    UpdateValueFunction(parent, node, alpha)
                if result != None:
                    parent = None
                else:
                    parent = node.clone()
            if result == None:
                move = RandomMove(node)
                node.play(*move)
                result = node.isGameOver()
        UpdateTerminalNode(node, result)
        if parent != None:
            UpdateValueFunction(parent, node, alpha)
    return BestMove(root)

def main():
    seed()
    win = GraphWin('TD-Learning(0) for TicTacToe', 600, 600, autoflush=False)
    ttt = TicTacToe()
    tttdraw = TTTDraw(win)
    tttinput = TTTInput(win)
    tttdraw.draw(ttt)
    
    try:
        vfile = open('ValueFunction.dat', 'rb')
        V = pickle.load(vfile)
        vfile.close()
    except FileNotFoundError:
        V = {}
    
        #Start to self-play
        self_play = 100
        for i in range(self_play):
            tmp_root = ttt.clone()
            tttdraw.draw(tmp_root)
            result = tmp_root.isGameOver()
            while result == None:
                move = TD0(tmp_root, V, 0.5, 0.1, 2000)
                #moves = tmp_root.getAllMoves()
                #move = moves[randint(0, len(moves)-1)]
                if move != ():
                    tmp_root.play(*move)
                tttdraw.draw(tmp_root)
                result = tmp_root.isGameOver()
                if result == None:
                    move = TD0(tmp_root, V, 0.5, 0.1, 2000)
                    if move != ():
                        tmp_root.play(*move)
                tttdraw.draw(tmp_root)
                result = tmp_root.isGameOver()
                if result != None:
                    time.sleep(0.5)
        #Save V to file
        vfile = open('ValueFunction.dat', 'wb')
        pickle.dump(V, vfile)
        vfile.close()
    
    while win.checkKey() != 'Escape':
        if ttt.getPlayer() == TicTacToe.WHITE:
            move = TD0(ttt, V, 0.2, 0.1, 500)
            if move != ():
                ttt.play(*move)
        tttinput.input(ttt)
        tttdraw.draw(ttt)
        if ttt.isGameOver() != None:
            time.sleep(1)
            ttt.reset()
            tttdraw.draw(ttt)
            #win.getMouse()
    win.close()
    
if __name__ == '__main__':
    main()