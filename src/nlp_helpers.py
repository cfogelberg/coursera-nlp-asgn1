'''
common -- Commonly used snippets

This file is part of assignment 1 for Michael Collin's NLP Coursera 
course, 02-04/2013 (MCNLP).

MCNLP is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MCNLP is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MCNLP.  If not, see <http://www.gnu.org/licenses/>.

@author:     cfogelberg

@copyright:  2013 Christopher Fogelberg. All rights reserved.
        
@license:    GPL

@contact:    cfogelberg@gmail.com
@deffield    updated: Updated
'''
import logging
import common
import operator

class CountsFile:
    '''
    Loads output of count_freqs.py for arg max emission parameters
    '''
    _counts = {}
    _filename = ''
    _tag_list = []
    
    def __init__(self, filename, tag_list):
        self._filename = filename
        self._tag_list = tag_list
        self.load()
    
    def load(self):
        '''
        Loads file self._filename
        '''
        try:
            with open(self._filename, 'r') as f:
                for line in f:
                    self._load_count(line)
        except IOError:
            logging.error('Could not open {0}'.format(self._filename))
            raise
    
    def __getitem__(self, key):
        '''
        Returns count of key, e.g. count of 'O' or 'O Americans'
        '''
        if key in self._counts:
            return self._counts[key]
        else:
            return 0
    
    def _load_count(self, fileline):
        splitline = fileline.split()
        count = splitline[0]
        key = ' '.join(splitline[2:])
        self._counts[key] = float(count)
    
    def emission_parameter(self, count_wordtag, count_tag):
        '''
        Uses the count of a wordtag x and count of a tag y to calc e(x|y)
        
        E.g. the 2 in '2 WORDTAG O Americans' and the 345128 in 
        '345128 1-GRAM O'
        '''
        if count_wordtag in self._counts:
            return self[count_wordtag] / self[count_tag]
        else:
            return 0
    
    def transition_probability(self, trigram, bigram):
        '''
        Returns q(y_i | y_{i-2}, y_{i-1} using counts
        
        Uses * to denote y_{i-1} and y_0, and STOP as the tag for y_{n+1}.
        Parameters are white-space delimited tag strings.
        '''
        if trigram in self._counts:
            return self[trigram] / self[bigram]
        else:
            return 0
    
    def arg_max_tag(self, word):
        '''
        Returns arg-max tag for the word /word/, given the counts
        '''
        candidates = set(map(lambda tag: '{0} {1}'.format(tag, word), self._tag_list))
        if len(candidates & set(self._counts.keys())) == 0:
            logging.info("{0} is a rare word".format(word))
            return self.arg_max_tag('_RARE_')
        else:
            tag_probs = {}
            for tag in self._tag_list:
                tag_probs[tag] = self.emission_parameter(tag + ' ' + word, tag)
    
            max_tag = max(tag_probs.iterkeys(), key=(lambda key: tag_probs[key]))
            max_prob = tag_probs[max_tag]
            
            if max_prob == 0:
                raise Exception('Word {0} has 0 probability but is in self._tag_list')
            else:
                return max_tag



class InputFileWordCounts(object):
    '''
    Stores the word counts from a test (word-only) file in a map
    ''' 
    _counts = {}

    def __init__(self, filename):
        '''
        Loads a InputFileWordCounts object from a _word_tag_pairs file.
        '''
        try:
            with open(filename, 'r') as f:
                for line in f:
                    self._load_wordtag(line)
        except IOError:
            logging.error('Could not open {0}'.format(filename))
            raise
    
    def __getitem__(self, word):
        '''
        Returns count of word /word/, raises an Exception error if not object
        '''
        if word in self._counts:
            return self._counts[word]
        else:
            return 0
    
    def _load_wordtag(self, line):
        line = line.strip()
        if len(line) != 0:
            #word, tag = line.split()
            word = line
            if word in self._counts:
                self._counts[word] += 1
            else:
                self._counts[word] = 1
    
    def counts(self, word):
        if word in self._counts:
            return self._counts[word]
        else:
            return 0



class TestFile(object):
    '''
    Represents a test file (words, punctuation, sentence gaps) in memory.
    
    Allows loading, saving and some operations on it.
    '''
    _word_tag_pairs = []
    _filename = ''
    
    def __init__(self, filename):
        '''
        Sets _filename of training file and loads it
        '''
        self._filename = filename
        self.load()
    
    def __getitem__(self, i):
        '''
        Returns the word at position /i/ or throws an Exception if out of range
        '''
        if i < len(self._word_tag_pairs):
            return self._word_tag_pairs[i]
        else:
            raise Exception('Index {0} out of range [0..{1}]'.format(i, len(self._word_tag_pairs)-1))
    
    def load(self):
        '''
        Loads file self._filename
        '''
        try:
            with open(self._filename, 'r') as f:
                for line in f:
                    self._word_tag_pairs.append(line.strip())
        except IOError:
            logging.error('Could not open {0}'.format(self._filename))
            raise
    
    def save(self, filename = None):
        '''
        Saves file to provided path. Uses self._filename in case of None.
        '''
        if(filename == None):
            filename = self._filename
        
        with open(filename, 'w') as f:
            for word in self._word_tag_pairs:
                f.write(word + '\n')
                
    def print_words(self):
        '''
        Prints _word_tag_pairs/sentence breaks in file to screen, one per line
        '''
        for word in self._word_tag_pairs:
            print "'{0}'".format(word)
    
    def replace_rare_words(self, counts, threshold, replacement):
        '''
        Replaces all _word_tag_pairs in document that occur less than /threshold/ times
        with /replacement/ (gets word counts from /counts/ parameter)
        '''
        for i, word in enumerate(self._word_tag_pairs[:]):
            if counts[word] < threshold and word != '':
                self._word_tag_pairs[i] = replacement
    
    def tag_and_save_argmax(self, cf, savepath):
        '''
        Tags using the argmax, CountsFile /cf/ and saves to /savepath/
        '''
        with open(savepath, 'w') as f:
            for word in self._word_tag_pairs:
                if word.strip() == '':
                    f.write('\n')
                else:
                    f.write("{0} {1}\n".format(word, cf.arg_max_tag(word)))

    def tag_and_save_viterbi(self, cf, savepath):
        '''
        Tags using the Viterbi alg, CountsFile /cf/ and saves to /savepath/
        '''
        with open(savepath, 'w') as f:
            pass


class TrainingFile(object):
    '''
    Represents a labelled training file of words, punctuation and sentence gaps.
    
    Allows loading, saving and some operations on it.
    '''
    _word_tag_pairs = []
    _filename = ''
    _tag_list = []
    
    def __init__(self, filename, tag_list):
        '''
        Sets _filename of training file and loads it
        '''
        self._filename = filename
        self._tag_list = tag_list
        self.load()
    
    def __getitem__(self, i):
        '''
        Returns the word/tag tuple at /i/ or throws an Exception if out of range
        '''
        if i < len(self._word_tag_pairs):
            return self._word_tag_pairs[i]
        else:
            raise Exception('Index {0} out of range [0..{1}]'.format(i, len(self._word_tag_pairs)-1))
            
    def get_word(self, i):
        '''
        Returns the word at /i/ or throws an Exception if out of range
        '''
        if i < len(self._word_tag_pairs):
            return self._word_tag_pairs[i][0]
        else:
            raise Exception('Index {0} out of range [0..{1}]'.format(i, len(self._word_tag_pairs)-1))

    def get_tag(self, i):
        '''
        Returns the word at /i/ or throws an Exception if out of rangelen
        '''
        if i < len(self._word_tag_pairs):
            return self._word_tag_pairs[i][1]
        else:
            raise Exception('Index {0} out of range [0..{1}]'.format(i, len(self._word_tag_pairs)-1))
    
    def load(self):
        '''
        Loads file from self._filename
        '''
        try:
            with open(self._filename, 'r') as f:
                for line in f:
                    self._load_line(line)
        except IOError:
            logging.error('Could not open {0}'.format(self._filename))
            raise
    
    def _load_line(self, line):
        line = line.strip()
        if len(line) > 0:
            word_tag_pair = line.strip().split()
            self._word_tag_pairs.append(word_tag_pair)
        else:
            self._word_tag_pairs.append([])
    
    def save(self, filename = None):
        '''
        Saves file to provided path. Uses self._filename in case of None.
        '''
        if(filename == None):
            filename = self._filename

        with open(filename, 'w') as f:
            for word_tag_pair in self._word_tag_pairs:
                f.write(' '.join(word_tag_pair) + '\n')
                
    def print_words(self):
        '''
        Prints _word_tag_pairs/sentence breaks in file to screen, one per line
        '''
        for word_tag_pair in self._word_tag_pairs:
            print word_tag_pair
    
    def replace_rare_words(self, counts, threshold, replacement):
        '''
        Replaces all words in document that occur less than /threshold/ times 
        with /replacement/, grouping all taggings of word together (gets word
        counts from /counts/ parameter, summing counts of all possible tags)
        '''
        # New version, replaces rare words, not rare word-tag pairs:
        ######################################################################
        for i, word_tag_pair in enumerate(self._word_tag_pairs[:]):
            wtp_string = ' '.join(word_tag_pair)
            if wtp_string != '':
                word = word_tag_pair[0]
                all_word_tag_pairs = map(lambda tag: '{0} {1}'.format(word, tag), self._tag_list)
                word_count = sum(map(lambda word_tag_pair: counts[word_tag_pair], all_word_tag_pairs))
                if word_count < threshold:
                    self._word_tag_pairs[i][0] = replacement
        '''
        # Original version, replaces rare word-tag pairs, not rare words:
        ######################################################################
        for i, word_tag_pair in enumerate(self._word_tag_pairs[:]):
            wtp_string = ' '.join(word_tag_pair)
            if counts[wtp_string] < threshold and wtp_string != '':
                self._word_tag_pairs[i][0] = replacement
        '''