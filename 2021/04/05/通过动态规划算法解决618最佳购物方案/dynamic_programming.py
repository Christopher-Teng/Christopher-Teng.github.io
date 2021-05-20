# !/usr/bin/python3
# -*- coding:utf-8 -*-

TOTAL_ASSETS = 10000  # 总资产
RATE = 0.7  # 使用百分比
AVAILABLE_ASSET = TOTAL_ASSETS*RATE  # 可用资产
COMMODITY_LIST = {
    # 可选商品列表
    '苏泊尔电饭煲': (319, 10),
    '海尔净水器': (1188, 8),
    '海尔智能门锁': (1399, 9),
    '九阳破壁机': (449, 5),
    '海尔智能音箱': (199, 3),
    '海尔冰箱': (3199, 10),
    '海尔滚筒洗衣机': (2699, 10),
    '格力空气循环扇': (399, 6),
    '苏泊尔电压力锅': (259, 7),
    '碧然德滤水壶': (219, 5)
}


def generate_shopping_list(money, commodities):
    """
    指定可用金额作为约束条件，从提供的可选商品中选择出最佳选择方式，获取最多的需求值
    """
    current_asset = [
        i+100 for i in range(0, int(money), 100)]  # 将可用资产以100为最小单位进行划分
    commodity_names = list(commodities.keys())  # 所有可选商品
    selected_goods = [[set() for _ in current_asset]
                      for _ in commodity_names]  # 每个单元格中选中的商品，初始为空
    table = [[0 for _ in current_asset]
             for _ in commodity_names]  # 用于动态规划计算的网格

    def update_cells(row, column):
        """
        更新单元格的方法，传入当前单元格的行、列数
        """
        current_commodity = commodity_names[row]  # 当前商品名
        (price, grade) = commodities[current_commodity]  # 当前商品价格和需求值
        asset = current_asset[column]  # 当前可用金额
        if row == 0:  # 第一次计算的时候
            if asset >= price:  # 当前可用金额大于等于当前商品价格
                table[row][column] = grade  # 更新当前单元格数值
                selected_goods[row][column].add(
                    current_commodity)  # 更新当前单元格选择商品
        else:
            if asset >= price:  # 当前可用金额大于等于当前商品价格
                remaining_asset = asset-price  # 剩余金额
                # 最大的剩余可用金额，这里比如手中还剩371，则对应最大的剩余可用金额是300
                max_remaining_available_asset = (remaining_asset//100)*100
                remaining_asset_index = -1 if max_remaining_available_asset == 0 else current_asset.index(
                    max_remaining_available_asset)
                # 剩余金额可以获得的需求值
                remainder_grade = table[commodity_index -
                                        1][remaining_asset_index] if remaining_asset_index > -1 else 0
                current_total_grade = grade+remainder_grade  # 当前商品需求值和剩余金额可获得需求值之和
                # 本列上一行单元格的值，即当前可用金额下，前一次计算所得的最大需求值
                prev_grade = table[row-1][column]
                if current_total_grade >= prev_grade:  # 更新当前单元格
                    table[row][column] = current_total_grade
                    if remaining_asset_index > -1:  # 选择当前商品后，并且剩余金额大于等于100
                        prev_selected_goods = selected_goods[row -
                                                             1][remaining_asset_index].copy()
                        prev_selected_goods.add(current_commodity)
                        # 更新当前单元格选择的商品
                        selected_goods[row][column] = prev_selected_goods
                    else:  # 选择当前商品后，剩余金额不足100
                        selected_goods[row][column] = {
                            current_commodity}
                else:
                    table[row][column] = table[row-1][column]
                    selected_goods[row][column] = selected_goods[row -
                                                                 1][column].copy()
            else:
                # 当前可用金额小于当前商品价格时
                # 更新当前单元格需求值为上一次计算结果
                table[row][column] = table[row-1][column]
                # 更新当前单元格选择商品为上一次计算结果
                selected_goods[row][column] = selected_goods[row -
                                                             1][column].copy()

    for commodity_index in range(len(commodity_names)):  # 遍历每一行，即每种可选商品
        for asset_index in range(len(current_asset)):  # 遍历每一列，即每一档可用金额
            update_cells(commodity_index, asset_index)  # 更新单元格

    return {'选择的商品': selected_goods[-1][-1], '获得的需求值': table[-1][-1]}


print(generate_shopping_list(AVAILABLE_ASSET, COMMODITY_LIST))
