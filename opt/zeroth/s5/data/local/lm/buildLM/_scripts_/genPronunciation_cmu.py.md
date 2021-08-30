## genPronunciation_cmu.py

> AI-Hub kspon speech related scripts



변경사항: **line 1700 **(filename:~)

- 변경 전 (line 1699~ 1703)

```sh
def main():
    filename='buildLM/_scripts_/cmudict-0.7b.txt'
    if not os.path.exists(filename):
        print('No dictionary file: %s' % filename)
        sys.exit()
```



- 변경 후 (line 1699~1703)

```sh
def main():
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cmudict-0.7b.txt')
    if not os.path.exists(filename):
        print('No dictionary file: %s' % filename)
        sys.exit()
```



