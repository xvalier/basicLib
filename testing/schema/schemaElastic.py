#INDEX SCHEMA-------------------------------------------------------------------
#These settings determine the filters, analyzers, and schema for indexed documents
def compileIndex():
    indexSchema = {
    	"settings": {
    		"number_of_shards":1,
    		"analysis": {
    			#Filters are used to add/remove or parse individual terms
    			"filter":{
    				#Filters out clutter words that do not impact relevance
    				"stop":{
    					"type":"stop",
    					"stopwords":[
    						"a","an","are","as","at","be","but", "by", "is", "it",
    						"such", "that", "the", "their", "then", "there", "these",
    						"they", "this", "to", "was", "will", "with", "not"
    					]
    				},
    				#Trims all English words to their root word, normalizes tenses/conjugations
    				"stemExclusion":{
    					"type":"keyword_marker",
    					"keywords":[]
    				},
    				#Prevents specified words from being stemmed
    				"stem":{
    					"type":"stemmer",
    					"language":"english"
    				},
    				#Augments scores if phrase of specified length is matched
    				"shingles4":{
    					"type":"shingle",
    					"max_shingle_size":4,
    					"min_shingle_size":4,
    					"output_unigrams":"false"
    				},
    				"shingles3":{
    					"type":"shingle",
    					"max_shingle_size":3,
    					"min_shingle_size":3,
    					"output_unigrams":"false"
    				},
    				"shingles2":{
    					"type":"shingle",
    					"max_shingle_size":2,
    					"min_shingle_size":2,
    					"output_unigrams":"false"
    				},
    				#Prevents score from increasing due to repeat instances of relevant words
    				"removeDuplicates":{
    					"type":"unique",
    					"only_on_same_position":"false"
    				},
    				#Augments score if word has same meaning as another more relevant word
    				"synonymDirect":{
    					"type":"synonym",
    					"synonyms_path": "syn_con.txt"
    				},
    				#Augments score if word is related to other words (or in same category)
    				"synonymGenre":{
    					"type":"synonym",
    					"synonyms_path": "syn_exp.txt"
    				}
    			},
    			#Analyzers are a combination of tokenizers and a collection of filters
    			#Tokenizers determine which characters are 'counted' and how words are delimited
    			"analyzer":{
    				#Standard combination of filters for matching query terms against doc terms
    				"general":{
    					"type": "custom",
    					"tokenizer": "standard",
    					"filter": ["lowercase", "stop", "stemExclusion", "stem", "removeDuplicates"]
    				},
    				#Combines standard analyzer with augmented score for direct synonyms
    				"synonyms":{
    					"type":"custom",
    					"tokenizer":"standard",
    					"filter":["lowercase","stop","stemExclusion","stem","synonymDirect", "removeDuplicates"]
    				},
    				#Combines standard analyzer with augmented score for category words
    				"category":{
    					"type":"custom",
    					"tokenizer":"standard",
    					"filter":["lowercase","stop","stemExclusion","stem","synonymGenre", "removeDuplicates"]
    				},
    				#Used to match a phrase of specified length exactly with doc phrases
    				"phrase4":{
    					"type":"custom",
    					"tokenizer":"standard",
    					"filter":["lowercase","shingles4"]
    				},
    				"phrase3":{
    					"type":"custom",
    					"tokenizer":"standard",
    					"filter":["lowercase","shingles3"]
    				},
    				"phrase2":{
    					"type":"custom",
    					"tokenizer":"standard",
    					"filter":["lowercase","shingles2"]
    				}
    			}
    		}
    	},
    	#Mappings determine the document schema, and pairs analyzers to specific document fields to process
    	"mappings":{
    		"symptom":{
    			"properties":{
    				"id":{
    					"type":"integer",
    					"coerce":"true"
    				},
    				#description field has three different analyzers, one with best becomes overall score
    				"description":{
    					"fields":{
    						"general":{
    							"type":"text",
    							"analyzer":"general"
    						},
    						"category":{
    							"type":"text",
    							"analyzer":"category"
    						},
    						"synonyms":{
    							"type":"text",
    							"analyzer":"synonyms"
    						}
    					},
    					"type":"text"
    				},
    				#Error Codes need to match exact to have good score
    				"errCode":{
    					"type":"text",
    					"analyzer":"phrase2"
    				},
    				#Phrases only use phrase filters. The closer to exact match, the higher the score
    				"phrase":{
    					"fields":{
    						"4word":{
    							"type":"text",
    							"analyzer":"phrase4"
    						},
    						"3word":{
    							"type":"text",
    							"analyzer":"phrase3"
    						},
    						"2word":{
    							"type":"text",
    							"analyzer":"phrase2"
    						}
    					},
    					"type":"text"
    				},
    				#Keywords have same analyzers as description
    				"keywords":{
    					"fields":{
    						"general":{
    							"type":"text",
    							"analyzer":"general"
    						},
    						"category":{
    							"type":"text",
    							"analyzer":"category"
    						},
    						"synonyms":{
    							"type":"text",
    							"analyzer":"synonyms"
    						}
    					},
    					"type":"text"
    				},
    			}
    		}
    	}
    }
    return indexSchema

#QUERY SCHEMA-------------------------------------------------------------------
#These settings determine how to calculate match score between query and index documents
def compileQuery(description):
    querySchema = {
        #Determine which fields are relevant, max number of results, and min score cutoff
        "_source": ["id", "description", "phrase", "keywords"],
        "size":5,
        "min_score": 50,
        "query":{
            "bool":{
                #Score boost for queries that match indexed document descriptions more closely
                "should":[
                    #boost based on close description match
                    {
                        "multi_match": {
                            "query": description,
                            "type":"most_fields",
                            #Search using multiple analyzers, keep best score
                            "fields": [
                                "description.general",
                                "description.category",
                                "description.synonyms"
                            ],
                            #Cutoff for minimum term match for score to be contributed
                            "minimum_should_match": "70%",
                            #Reduce score contribution from common words
                            "cutoff_frequency":0.5,
                            #Multipier for entire clause
                            "boost":2.0
                        }
                    },
                    #Boost based on close keyword match
                    {
                        "match":{
                            "keywords.general":{
                                "query": description,
                                "boost": 10
                            }
                        }
                    },
                    #Boost based on keyword synonym boost
                    {
                        "multi_match":{
                            "query": description,
                            "type":"most_fields",
                            "fields": [
                                "keywords.category",
                                "keywords.synonyms"
                            ],
                            "boost":3
                        }
                    },
                    #boost based on exact error code match
                    {
                        "match":{
                            "errCode":{
                                "query": description,
                                "boost": 100
                            }
                        }
                    },
                    #Boost for phrases (higher number of exact words in sequence = bigger multiplier)
                    {
                        "match":{
                            "phrase.4word":{
                                "query": description,
                                "boost": 50
                            }
                        }
                    },

                    {
                        "match":{
                            "phrase.3word":{
                                "query": description,
                                "boost": 25
                            }
                        }
                    },
                    {
                        "match":{
                            "phrase.2word":{
                                "query": description,
                                "boost": 5
                            }
                        }
                    }
                ],
                #Base score from broad query
                "must":[
                    {
                        "multi_match":{
                            "query": description,
                            "type":"most_fields",
                            "fields": [
                                "description.general",
                                "description.category",
                                "description.synonyms"
                            ],
                            "minimum_should_match": "10%",
                            "cutoff_frequency":0.1,
                            #Used to account for spelling mistakes
                            "fuzziness": "AUTO"
                        }
                    }
                ]
            }
        },
    }
    return querySchema
