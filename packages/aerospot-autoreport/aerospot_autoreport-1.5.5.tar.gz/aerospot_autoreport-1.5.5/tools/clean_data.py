import pandas as pd
import numpy as np
import os





if __name__ == "__main__":
    dir_path = r"D:\OneDrive_yzuzhny\study\AutoReportV3\武汉\merged_output"
    
    indexs_data = pd.read_csv(os.path.join(dir_path, "INDEXS.csv"), index_col=0, header=0)
    pos_data = pd.read_csv(os.path.join(dir_path, "POS.txt"), header=None)

    for col_name in indexs_data.columns:

        value_data = indexs_data[col_name]
        # 用突变百分比超过前后共10个值的均值百分之20为标准筛选异常值
        window = 5  # 前后各5个，共10个
        outlier_indices = []
        values = value_data.values
        indices = value_data.index.values
        for i in range(len(values)):
            # 获取前后各5个的均值（不包括自身）
            start = max(0, i - window)
            end = min(len(values), i + window + 1)
            neighbor_values = np.delete(values[start:end], i - start)
            if len(neighbor_values) == 0:
                continue
            neighbor_mean = np.mean(neighbor_values)
            if neighbor_mean == 0:
                continue
            diff_percent = abs(values[i] - neighbor_mean) / abs(neighbor_mean)
            if diff_percent > 0.6:
                outlier_indices.append(indices[i])
        print(col_name,outlier_indices)



