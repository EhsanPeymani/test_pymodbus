from decoder import RegisterCountParams, DataType, DataDecoder


x = DataDecoder.get_register_count(data_type=DataType.UINT64, string_length=10)
print(x)