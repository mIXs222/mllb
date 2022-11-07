import json
import pandas as pd

def into_json_gen(paths):
  for path in paths:
    with open(path, 'r') as f:
      for line in f:
        try:
          logline = json.loads(line)
          yield logline
        except Exception as e:
          pass  # ignore non-json line

def combine_dict(dict_gen):
  all_logline = None
  for logline in dict_gen:
    if all_logline is None:
      all_logline = {}
      for key in logline: all_logline[key] = [logline[key]]
    else:
      assert all_logline.keys() == logline.keys()
      for key in logline: all_logline[key].append(logline[key])
  return all_logline


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Combine cdb json result by operation.')
  parser.add_argument('jsons', metavar='N', type=str, nargs='+',
                      help='path to jsons output')
  parser.add_argument('--out', type=str, default=None,
                      help='path to save output csv')
  args = parser.parse_args()
  df = pd.DataFrame.from_dict(combine_dict(into_json_gen(args.jsons)))
  print(df)

  if args.out:
    df.to_csv(args.out)
    print(f"Saved to {args.out}")
