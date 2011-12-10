#!/usr/bin/python3

import argparse, html.parser, os, re, sys, urllib.parse, urllib.request

parser = argparse.ArgumentParser(description='Codeforces scraper.  https://github.com/lovrop/codeforces-scraper')
parser.add_argument('contest', help='URI or numerical ID of contest to scrape')
args = parser.parse_args()

# See if it was just a numeric ID
try:
    contest_id = int(args.contest)
    contest_uri = 'http://codeforces.com/contest/{}'.format(contest_id)
except ValueError:
    contest_uri = args.contest

print('Retrieving ', contest_uri, '... ', sep='', end='')
sys.stdout.flush()
contest_html = urllib.request.urlopen(contest_uri).read().decode('utf-8')
print('OK ({} bytes).'.format(len(contest_html)))

class ContestHTMLParser(html.parser.HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.problems = set()
        self.re = re.compile('contest/\d+/problem/(\w+)')
    
    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        
        href = dict(attrs).get('href')
        if not href:
            return

        match = self.re.search(href)
        if not match:
            return

        self.problems.add(match.group(1))

    def getProblems(self):
        return sorted(list(self.problems))

class ProblemHTMLParser(html.parser.HTMLParser):
    class Node:
        def __init__(self, tag, attrs):
            self.tag = tag
            self.attrs = attrs
            self.children = []
            self.data = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stack = []
        self.sample_input_nodes = []
        self.recording = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        sample_input_div = tag == 'div' and attrs.get('class', '').find('sample') != -1
        if self.recording or sample_input_div:
            self.recording = True
            node = ProblemHTMLParser.Node(tag, attrs)
            if self.stack:
                if tag == 'br':
                    self.stack[-1].data += '\n'
                else:
                    self.stack[-1].children.append(node)
            self.stack.append(node)

    def handle_endtag(self, tag):
        if self.recording:
            node = self.stack.pop()
            if not self.stack:
                self.sample_input_nodes.append(node)
                self.recording = False

    def handle_data(self, data):
        if self.recording:
            self.stack[-1].data += data

    def walkNodes(self, node, output_pre_datas):
        if node.tag == 'pre':
            output_pre_datas.append(node.data)
        else:
            for child in node.children:
                self.walkNodes(child, output_pre_datas)

    def getExamples(self):
        if not self.sample_input_nodes:
            return []

        assert len(self.sample_input_nodes) == 1

        pre_datas = []
        self.walkNodes(self.sample_input_nodes[0], pre_datas)

        assert len(pre_datas) % 2 == 0

        examples = []
        for i in range(0, len(pre_datas), 2):
            examples.append((pre_datas[i], pre_datas[i+1]))
        return examples

parser = ContestHTMLParser()
parser.feed(contest_html)
problems = parser.getProblems()

print('Found', len(problems), 'problems.')

for problem in problems:
    problem_uri = contest_uri + '/problem/' + problem
    print('Retrieving ', problem_uri, '... ', sep='', end='')
    sys.stdout.flush()
    problem_html = urllib.request.urlopen(problem_uri).read().decode('utf-8')
    print('OK ({} bytes).'.format(len(problem_html)))

    # Hack for codeforces HTML error
    problem_html = problem_html.replace('<p</p>', '<p></p>')
    
    parser = ProblemHTMLParser()
    parser.feed(problem_html)

    examples = parser.getExamples()

    problem_dir = problem.lower()
    if not os.path.isdir(problem_dir):
        os.mkdir(problem_dir)

    for i, example in enumerate(examples, 1):
        input_path = os.path.join(problem_dir, 'in{}'.format(i))
        with open(input_path, 'w') as f:
            f.write(example[0])

        output_path = os.path.join(problem_dir, 'out{}'.format(i))
        with open(output_path, 'w') as f:
            f.write(example[1])

    print('Wrote {} examples for problem {}.'.format(len(examples), problem))