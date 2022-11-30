import pickle

def parse_pickle(path):
  with open(path, 'rb') as f:
    return pickle.load(f)

def write_text(param, path):
  with open(path, 'w') as f:
    for key, value in param.items():
      print(f"Writing {key}, shape= {value.shape}")
      f.write(f"{key}\n")
      if len(value.shape) == 1:  # vectors
        f.write(f"{1} {value.shape[0]}\n")
        for elem in row:
          f.write(f"{elem} ")
        f.write(f"\n")
      elif len(value.shape) == 2:  # matrices
        f.write(f"{value.shape[0]} {value.shape[1]}\n")
        for row in value:
          for elem in row:
            f.write(f"{elem} ")
          f.write(f"\n")
      else:
        raise ValueError(f"Unsupported tensor shape: {value.shape}")


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Parse pickle parameter file into text file')
  parser.add_argument('in_pickle', type=str,
                      help='path to pickle parameter file')
  parser.add_argument('out_txt', type=str,
                      help='path to save text parameter file')
  args = parser.parse_args()

  param = parse_pickle(args.in_pickle)
  print(f'Loaded parameters: {param}')

  write_text(param, args.out_txt)
  print(f'Wrote parameters into {args.out_txt}')
