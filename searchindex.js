Search.setIndex({envversion:47,filenames:["about","api/lovett","api/lovett.compat","api/lovett.corpus","api/lovett.db","api/lovett.ilovett","api/lovett.loader","api/lovett.query","api/lovett.transform","api/lovett.tree","api/lovett.util","api/modules","example-usage","index","indexing"],objects:{"":{lovett:[1,0,0,"-"]},"lovett.compat":{strip_corpussearch_comments:[2,4,1,""]},"lovett.corpus":{Corpus:[3,2,1,""],CorpusBase:[3,2,1,""]},"lovett.corpus.Corpus":{"__delitem__":[3,3,1,""],"__getitem__":[3,3,1,""],"__init__":[3,3,1,""],"__len__":[3,3,1,""],"__repr__":[3,3,1,""],"__setitem__":[3,3,1,""],"__str__":[3,3,1,""],"_repr_html_":[3,3,1,""],insert:[3,3,1,""],to_db:[3,3,1,""],write_penn_treebank:[3,3,1,""]},"lovett.corpus.CorpusBase":{matching_trees:[3,3,1,""]},"lovett.db":{CorpusDb:[4,2,1,""]},"lovett.db.CorpusDb":{"__getitem__":[4,3,1,""],"__init__":[4,3,1,""],"__len__":[4,3,1,""],"_add_child":[4,3,1,""],"_add_sibling":[4,3,1,""],"_insert_node":[4,3,1,""],"_reconstitute":[4,3,1,""],dom:[4,1,1,""],engine:[4,1,1,""],insert_tree:[4,3,1,""],metadata:[4,1,1,""],nodes:[4,1,1,""],roots:[4,1,1,""],sprec:[4,1,1,""],to_corpus:[4,3,1,""]},"lovett.ilovett":{ilovett:[5,4,1,""]},"lovett.loader":{FileLoader:[6,2,1,""],GithubLoader:[6,2,1,""],ICEPAHC:[6,5,1,""],Loader:[6,2,1,""]},"lovett.loader.FileLoader":{"__init__":[6,3,1,""],file:[6,3,1,""],files:[6,3,1,""]},"lovett.loader.GithubLoader":{"__init__":[6,3,1,""],clear_cache:[6,3,1,""],fetch_all:[6,3,1,""],file:[6,3,1,""],files:[6,3,1,""]},"lovett.loader.Loader":{corpus:[6,3,1,""],file:[6,3,1,""],files:[6,3,1,""]},"lovett.query":{And:[7,2,1,""],Not:[7,2,1,""],Or:[7,2,1,""],QueryFunction:[7,2,1,""],WrapperQueryFunction:[7,2,1,""],dash_tag:[7,2,1,""],doms:[7,2,1,""],idoms:[7,2,1,""],label:[7,2,1,""],sprec:[7,2,1,""]},"lovett.query.And":{"__init__":[7,3,1,""],"__str__":[7,3,1,""],match_tree:[7,3,1,""],sql:[7,3,1,""]},"lovett.query.Not":{"__init__":[7,3,1,""],"__str__":[7,3,1,""],match_tree:[7,3,1,""],sql:[7,3,1,""]},"lovett.query.Or":{"__init__":[7,3,1,""],"__str__":[7,3,1,""],match_tree:[7,3,1,""],sql:[7,3,1,""]},"lovett.query.QueryFunction":{"__and__":[7,3,1,""],"__invert__":[7,3,1,""],"__or__":[7,3,1,""],"__str__":[7,3,1,""],match_tree:[7,3,1,""],sql:[7,3,1,""]},"lovett.query.WrapperQueryFunction":{"__init__":[7,3,1,""],"__str__":[7,3,1,""],name:[7,1,1,""]},"lovett.query.dash_tag":{"__init__":[7,3,1,""],"__str__":[7,3,1,""],sql:[7,3,1,""],tag:[7,1,1,""]},"lovett.query.doms":{"__init__":[7,3,1,""],match_tree:[7,3,1,""],sql:[7,3,1,""]},"lovett.query.idoms":{"__init__":[7,3,1,""],match_tree:[7,3,1,""],sql:[7,3,1,""]},"lovett.query.label":{"__init__":[7,3,1,""],"__str__":[7,3,1,""],exact:[7,1,1,""],label:[7,1,1,""],match_tree:[7,3,1,""],sql:[7,3,1,""]},"lovett.transform":{"_icepahc_case_do":[8,4,1,""],ICEPAHC_CASES:[8,5,1,""],ICEPAHC_CASE_LABELS:[8,5,1,""],ensure_id:[8,4,1,""],icepahc_case:[8,4,1,""],icepahc_lemma:[8,4,1,""],icepahc_year:[8,4,1,""]},"lovett.tree":{"_check_metadata_name":[9,4,1,""],"_index_string_for_metadata":[9,4,1,""],"_postprocess_parsed":[9,4,1,""],"_tokenize":[9,4,1,""],Leaf:[9,2,1,""],Metadata:[9,2,1,""],NonTerminal:[9,2,1,""],ParseError:[9,6,1,""],Tree:[9,2,1,""],parse:[9,4,1,""]},"lovett.tree.Leaf":{"__eq__":[9,3,1,""],"__hash__":[9,1,1,""],"__init__":[9,3,1,""],"__repr__":[9,3,1,""],"__slots__":[9,1,1,""],"__str__":[9,3,1,""],"_repr_html_":[9,3,1,""],"_to_json_pre":[9,3,1,""],text:[9,1,1,""],urtext:[9,1,1,""]},"lovett.tree.Metadata":{"__delattr__":[9,3,1,""],"__delitem__":[9,3,1,""],"__getattr__":[9,3,1,""],"__getitem__":[9,3,1,""],"__init__":[9,3,1,""],"__iter__":[9,3,1,""],"__len__":[9,3,1,""],"__setattr__":[9,3,1,""],"__setitem__":[9,3,1,""],"__slots__":[9,1,1,""],"_dict":[9,1,1,""]},"lovett.tree.NonTerminal":{"__contains__":[9,3,1,""],"__delitem__":[9,3,1,""],"__eq__":[9,3,1,""],"__getitem__":[9,3,1,""],"__hash__":[9,1,1,""],"__init__":[9,3,1,""],"__iter__":[9,3,1,""],"__len__":[9,3,1,""],"__repr__":[9,3,1,""],"__setitem__":[9,3,1,""],"__slots__":[9,1,1,""],"__str__":[9,3,1,""],"_children":[9,1,1,""],"_repr_html_":[9,3,1,""],"_to_json_pre":[9,3,1,""],children:[9,1,1,""],insert:[9,3,1,""]},"lovett.tree.Tree":{"__eq__":[9,3,1,""],"__hash__":[9,1,1,""],"__init__":[9,3,1,""],"__repr__":[9,3,1,""],"__slots__":[9,1,1,""],"__str__":[9,3,1,""],"_label":[9,1,1,""],"_parent_index":[9,1,1,""],"_repr_html_":[9,3,1,""],"_to_json_pre":[9,3,1,""],id:[9,1,1,""],label:[9,1,1,""],left_sibling:[9,1,1,""],metadata:[9,1,1,""],parent:[9,1,1,""],right_sibling:[9,1,1,""],root:[9,1,1,""],to_json:[9,3,1,""],urtext:[9,1,1,""]},"lovett.util":{index:[10,4,1,""],index_type:[10,4,1,""],is_ec:[10,4,1,""],is_leaf:[10,4,1,""],is_nonterminal:[10,4,1,""],is_silent:[10,4,1,""],is_text_leaf:[10,4,1,""],is_trace:[10,4,1,""],is_trace_string:[10,4,1,""],label_and_index:[10,4,1,""],remove_index:[10,4,1,""],set_index:[10,4,1,""]},lovett:{compat:[2,0,0,"-"],corpus:[3,0,0,"-"],db:[4,0,0,"-"],ilovett:[5,0,0,"-"],loader:[6,0,0,"-"],query:[7,0,0,"-"],transform:[8,0,0,"-"],tree:[9,0,0,"-"],util:[10,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","attribute","Python attribute"],"2":["py","class","Python class"],"3":["py","method","Python method"],"4":["py","function","Python function"],"5":["py","data","Python data"],"6":["py","exception","Python exception"]},objtypes:{"0":"py:module","1":"py:attribute","2":"py:class","3":"py:method","4":"py:function","5":"py:data","6":"py:exception"},terms:{"0x7f035f7c6048":[],"0x7f035f7c60d0":[],"0x7f035f7c6510":[],"0x7f035f7c6ae8":[],"0x7f035f7c6b70":[],"0x7f035f7c6bf8":[],"0x7f035f9d2ae8":[],"0x7f0360ffb2f0":[],"0x7f0360ffb6a8":[],"0x7f036107c630":[],"0x7f036107c780":[],"0x7f0361132e48":[],"0x7f0361132e80":[],"0x7f0361132eb8":[],"0x7f0361142ac8":[],"0x7f0364e8d2f0":[],"0x7f0364e8d6a8":[],"0x7f0364ead598":[],"0x7f0364ead7b8":[],"0x7f0364ead840":[],"0x7f0364ead950":[],"0x7f0364eadc80":[],"0x7f0364eadd08":[],"0x7f03650a6bf8":[],"0x7f036673c438":[],"0x7f036673cc18":[],"0x7f03667a5ba8":[],"0x7f03667c9438":[],"0x7f03667c94e0":[],"0x7f03667c9668":[],"0x7f07a45432f0":[],"0x7f07a45436a8":[],"0x7f07a4552048":[],"0x7f07a4552620":[],"0x7f07a45526a8":[],"0x7f07a4552730":[],"0x7f07a45527b8":[],"0x7f07a4552840":[],"0x7f07a46dabf8":[],"0x7f07a5deb828":[],"0x7f07a5deba20":[],"0x7f07a5debc50":[],"0x7f07a5e71048":[],"0x7f07a5e710b8":[],"0x7f07a5e712b0":[],"0x7f0aacef62e8":[],"0x7f0aacef6978":[],"0x7f0aacef6e48":[],"0x7f0aacf389d8":[],"0x7f0aacf38ae8":[],"0x7f0aacf38b70":[],"0x7f0aacf38bf8":[],"0x7f0aacf38c80":[],"0x7f0aacf38d08":[],"0x7f0aad1439d8":[],"0x7f0aae7df268":[],"0x7f0aae7df620":[],"0x7f0aae7f6b38":[],"0x7f0aae7fa780":[],"0x7f0aae81b400":[],"0x7f0ce8d62da0":[],"0x7f0ce8d62dd8":[],"0x7f0ce8d62e10":[],"0x7f0ce8d9c048":[],"0x7f0ce8d9c0d0":[],"0x7f0ce8d9c158":[],"0x7f0ce8d9c1e0":[],"0x7f0ce8d9c268":[],"0x7f0ce8d9cbf8":[],"0x7f0ce8f9eae8":[],"0x7f0ce9c72510":[],"0x7f0ce9c726a8":[],"0x7f0cea66b358":[],"0x7f0cea66b630":[],"0x7f0cea66bb70":[],"0x7f0f863f42f0":[],"0x7f0f863f46a8":[],"0x7f0f865b69d8":[],"0x7f1636c79048":[],"0x7f1636c790d0":[],"0x7f1636c79400":[],"0x7f1636c79ae8":[],"0x7f1636c79b70":[],"0x7f1636c79bf8":[],"0x7f1636e8eae8":[],"0x7f16384c32f0":[],"0x7f16384c36a8":[],"0x7f163852ff28":[],"0x7f163856eb38":[],"0x7f163856ee80":[],"0x7f1638600c50":[],"0x7f1638600c88":[],"0x7f1638600f60":[],"0x7f1a483562f0":[],"0x7f1a483566a8":[],"0x7f1a483740d0":[],"0x7f1a483747b8":[],"0x7f1a48374840":[],"0x7f1a48374950":[],"0x7f1a48374c80":[],"0x7f1a48374d08":[],"0x7f1a48376320":[],"0x7f1a48376ba8":[],"0x7f1a48376d30":[],"0x7f1a48571bf8":[],"0x7f1a49c0b1d0":[],"0x7f1a49c0b208":[],"0x7f1a49c0b240":[],"0x7f1bad56d278":[],"0x7f1bad56d710":[],"0x7f1bad56d8d0":[],"0x7f1bad5ab378":[],"0x7f1bad5ab9d8":[],"0x7f1bad5abae8":[],"0x7f1bad5abb70":[],"0x7f1bad5abbf8":[],"0x7f1bad5abc80":[],"0x7f1bad7be9d8":[],"0x7f1baedd2268":[],"0x7f1baedd2620":[],"0x7f1baee07da0":[],"0x7f1baee07e80":[],"0x7f1baee07eb8":[],"0x7f2e04889240":[],"0x7f2e04889358":[],"0x7f2e04889400":[],"0x7f2e048d3048":[],"0x7f2e048d3d08":[],"0x7f2e048d3d90":[],"0x7f2e048d3e18":[],"0x7f2e048d3ea0":[],"0x7f2e048d3f28":[],"0x7f2e04ad9ae8":[],"0x7f2e060f32f0":[],"0x7f2e060f36a8":[],"0x7f2e061e3550":[],"0x7f2e061e3710":[],"0x7f2e061e3b70":[],"0x7f305eae9e48":[],"0x7f305eae9e80":[],"0x7f305eb20158":[],"0x7f305eb201e0":[],"0x7f305eb20268":[],"0x7f305eb206a8":[],"0x7f305eb20b70":[],"0x7f305eb20f28":[],"0x7f305ed29ae8":[],"0x7f30603313c8":[],"0x7f3060364a58":[],"0x7f3060364eb8":[],"0x7f30603f1cf8":[],"0x7f30604212f0":[],"0x7f30604216a8":[],"0x7f313ce83048":[],"0x7f313ce830d0":[],"0x7f313ce83158":[],"0x7f313ce831e0":[],"0x7f313ce83268":[],"0x7f313ce83bf8":[],"0x7f313d084ae8":[],"0x7f313e6cc240":[],"0x7f313e76b510":[],"0x7f313e76b6a8":[],"0x7f313e795d68":[],"0x7f313e795e10":[],"0x7f313e802eb8":[],"0x7f313e802ef0":[],"0x7f313e802f28":[],"0x7f35a3a25d30":[],"0x7f35a3a25dd8":[],"0x7f35a3a25f28":[],"0x7f35a3a52b70":[],"0x7f35a3a52c80":[],"0x7f35a3a52d08":[],"0x7f35a3a52d90":[],"0x7f35a3a52e18":[],"0x7f35a3a52ea0":[],"0x7f35a3c5aae8":[],"0x7f35a528b2f0":[],"0x7f35a528b6a8":[],"0x7f35a52ad550":[],"0x7f35a5308c50":[],"0x7f35a53cf208":[],"0x7f5d9b9582f0":[],"0x7f5d9b9586a8":[],"0x7f5d9bb6da60":[],"0x7f5d9bb8bac8":[],"0x7f5d9bb8bcc0":[],"0x7f5d9bb8bcf8":[],"0x7f5d9d210048":[],"0x7f5d9d210ef0":[],"0x7f5d9d26e1e0":[],"0x7f5d9d26e378":[],"0x7f5d9d26e7b8":[],"0x7f5d9d26e840":[],"0x7f5d9d26ec80":[],"0x7f5d9d26ed08":[],"0x7f5d9d29ee80":[],"0x7f733df5bef0":[],"0x7f733df5bf28":[],"0x7f733df83048":[],"0x7f733df830d0":[],"0x7f733df83158":[],"0x7f733df831e0":[],"0x7f733df83268":[],"0x7f733df83bf8":[],"0x7f733e18fae8":[],"0x7f733ee5e510":[],"0x7f733ee5e6a8":[],"0x7f733f7a3a58":[],"0x7f733f839710":[],"0x7f733f839fd0":[],"0x7f733f864da0":[],"0x7f7e61d9b3c8":[],"0x7f7e61d9b710":[],"0x7f7e61d9b8d0":[],"0x7f7e61dcd048":[],"0x7f7e61dcdd08":[],"0x7f7e61dcdd90":[],"0x7f7e61dcde18":[],"0x7f7e61dcdea0":[],"0x7f7e61dcdf28":[],"0x7f7e61fd8ae8":[],"0x7f7e63625a20":[],"0x7f7e636802f0":[],"0x7f7e636806a8":[],"0x7f7e636f3550":[],"0x7f7e636f39e8":[],"0x7f84f4ff81e0":[],"0x7f84f4ff8598":[],"0x7f84f52138c8":[],"0x7f84f521cba8":[],"0x7f84f6866cf8":[],"0x7f84f6866eb8":[],"0x7f84f68b4320":[],"0x7f84f68b4390":[],"0x7f84f68fa158":[],"0x7f84f68fa1e0":[],"0x7f84f68fa840":[],"0x7f84f68fa950":[],"0x7f84f68fa9d8":[],"0x7f84f68faa60":[],"0x7f84f692afd0":[],"0x7f881639e2f0":[],"0x7f881639e6a8":[],"0x7f88163ad048":[],"0x7f88163ad620":[],"0x7f88163ad6a8":[],"0x7f88163ad730":[],"0x7f88163ad7b8":[],"0x7f88163ad840":[],"0x7f88165b3bf8":[],"0x7f8817bf7588":[],"0x7f8817bf75f8":[],"0x7f8817c2fd68":[],"0x7f8817d164a8":[],"0x7f8817d16668":[],"0x7f8817d16d30":[],"0x7f960a330eb8":[],"0x7f960a330ef0":[],"0x7f960a330f28":[],"0x7f960a368048":[],"0x7f960a3680d0":[],"0x7f960a368158":[],"0x7f960a3681e0":[],"0x7f960a368268":[],"0x7f960a368bf8":[],"0x7f960a56bae8":[],"0x7f960b240510":[],"0x7f960b2406a8":[],"0x7f960bc39240":[],"0x7f960bc39f28":[],"0x7f960bc96d30":[],"0x7f9807fd7048":[],"0x7f9807fd70d0":[],"0x7f9807fd7400":[],"0x7f9807fd7ae8":[],"0x7f9807fd7b70":[],"0x7f9807fd7bf8":[],"0x7f9808023550":[],"0x7f98081e4ae8":[],"0x7f98098052f0":[],"0x7f98098056a8":[],"0x7f9809836828":[],"0x7f98098ffe48":[],"0x7f98099539b0":[],"0x7f98099593c8":[],"0x7f9809959470":[],"0x7fb43b122510":[],"0x7fb43b1226a8":[],"0x7fb43b13b048":[],"0x7fb43b13b0d0":[],"0x7fb43b13b158":[],"0x7fb43b13b1e0":[],"0x7fb43b13b268":[],"0x7fb43b13bbf8":[],"0x7fb43b339ae8":[],"0x7fb43ca09588":[],"0x7fb43ca09e48":[],"0x7fb43caa7e48":[],"0x7fb43caa7e80":[],"0x7fb43caa7eb8":[],"0x7fb43cab9c50":[],"0x7fb6edb74e10":[],"0x7fb6edb74e48":[],"0x7fb6edb98510":[],"0x7fb6edb986a8":[],"0x7fb6edbae048":[],"0x7fb6edbae0d0":[],"0x7fb6edbae158":[],"0x7fb6edbae1e0":[],"0x7fb6edbae268":[],"0x7fb6edbaebf8":[],"0x7fb6edbb0cf8":[],"0x7fb6eddaeae8":[],"0x7fb6ef46e6d8":[],"0x7fb6ef46edd8":[],"0x7fb6ef4ae3c8":[],"0x7fb73d05b730":[],"0x7fb73d05b7b8":[],"0x7fb73d05b840":[],"0x7fb73d05b8c8":[],"0x7fb73d05b950":[],"0x7fb73d05bd08":[],"0x7fb73d263a60":[],"0x7fb73e87e710":[],"0x7fb73e87e828":[],"0x7fb73e87ec50":[],"0x7fb73e8b3510":[],"0x7fb73e8b36a8":[],"0x7fb73e8f0908":[],"0x7fb73e8f0b00":[],"0x7fb73e913588":[],"0x7fbb710dc048":[],"0x7fbb710dc158":[],"0x7fbb710dc598":[],"0x7fbb710dc6a8":[],"0x7fbb710dc730":[],"0x7fbb710dc7b8":[],"0x7fbb710e09e8":[],"0x7fbb710e0c50":[],"0x7fbb710e0ef0":[],"0x7fbb712de9d8":[],"0x7fbb72922ef0":[],"0x7fbb729de488":[],"0x7fbb729de620":[],"0x7fbb72a50ba8":[],"0x7fbb72a50e80":[],"0x7fe9ccbcc2f0":[],"0x7fe9ccbcc6a8":[],"0x7fe9ccbeb0d0":[],"0x7fe9ccbeb7b8":[],"0x7fe9ccbeb840":[],"0x7fe9ccbeb950":[],"0x7fe9ccbebc80":[],"0x7fe9ccbebd08":[],"0x7fe9ccde7bf8":[],"0x7fe9ce47fac8":[],"0x7fe9ce4be160":[],"0x7fe9ce4f9358":[],"0x7fe9ce53f780":[],"0x7fe9ce53ff60":[],"0x7fe9ce53ffd0":[],"0x7ff5fe36d2f0":[],"0x7ff5fe36d6a8":[],"0x7ff5fe389598":[],"0x7ff5fe3897b8":[],"0x7ff5fe389840":[],"0x7ff5fe389950":[],"0x7ff5fe389c80":[],"0x7ff5fe389d08":[],"0x7ff5fe586bf8":[],"0x7ff5ffc18358":[],"0x7ff5ffc185c0":[],"0x7ff5ffc18c18":[],"0x7ff5ffc18cf8":[],"0x7ff5ffc88080":[],"0x7ff5ffc98f98":[],"___":7,"__abstractmethods__":[],"__and__":7,"__contains__":9,"__delattr__":9,"__delitem__":[3,9],"__dict__":[],"__doc__":[],"__eq__":9,"__getattr__":9,"__getitem__":[3,4,9],"__hash__":9,"__init__":[3,4,6,7,9],"__invert__":7,"__iter__":9,"__len__":[3,4,9],"__module__":[],"__or__":7,"__repr__":[3,9],"__setattr__":9,"__setitem__":[3,9],"__slots__":9,"__str__":[3,7,9],"__weakref__":[],"_abc_cach":[],"_abc_negative_cach":[],"_abc_negative_cache_vers":[],"_abc_registri":[],"_add_child":4,"_add_sibl":4,"_check_metadata_nam":9,"_children":9,"_dict":9,"_icepahc_case_do":8,"_index_string_for_metadata":9,"_insert_nod":4,"_label":9,"_nest":7,"_parent_index":9,"_postprocess_pars":9,"_reconstitut":4,"_repr_html_":[3,9],"_to_json_pr":9,"_token":9,"_weakrefset":[],"boolean":7,"case":[7,8,12],"class":[3,4,6,7,9,12],"default":[6,7,12],"final":[4,12],"function":[2,3,4,5,6,7,8,12],"import":12,"int":4,"long":[4,12],"new":[3,4,13],"public":12,"return":[2,3,4,6,7],"static":12,"super":6,"true":7,aaron:[0,12,13,14],abc:3,abov:3,access:[6,7,12],accommod:8,accus:8,accustom:12,across:3,add:[4,7,8],addit:3,advanc:13,advantag:12,aecai:[],against:[4,7],aid:12,aim:12,all:[6,7,12],all_verb:7,allow:[3,7,12],alreadi:[8,12],also:[3,4,6,7,12],altern:3,amount:12,analog:7,analys:12,analysi:[12,13],analyst:12,ani:[4,7],annotald:[3,13],anoth:7,anticip:13,antonkarl:12,appear:6,append:[4,7],appropri:[4,6,7,12],approxim:7,arbitrari:7,argument:[7,12],arithmet:7,arrang:4,aspect:12,associ:6,assum:[8,12],assumpt:4,attempt:[3,4],attent:7,attribut:[],audienc:13,author:[0,12,13,14],autom:13,avail:[6,12],avoid:12,back:3,backend:[],base:[3,6,12,13],basic:12,bear:8,becaus:[7,12],been:8,begin:8,behavior:7,belong:3,benefit:[4,12],better:7,between:[8,12],beyond:6,bia:7,bit:3,bitwis:7,blank:7,block:2,boilerpl:12,bool:[6,7],botani:12,bring:[4,12],browser:3,build:4,built:6,cach:6,call:[4,6],can:[3,6,7,8,12],candid:7,capabl:7,care:7,categori:8,caution:[],certain:8,chang:[3,7],charact:12,check:6,child:4,children:9,clear_cach:6,clutter:12,code:[6,12,13],collect:3,column:4,combinator:7,combinatori:12,comment:2,common:[6,7],commonli:12,compat:[],compos:6,compress:12,comput:12,conjoin:7,conjug:7,conjunct:7,conjunctuion:7,connect:13,consid:6,consol:3,constant:3,construct:[4,12],contain:[3,4,6,7,12],convention:8,convert:[4,6,8],corpora:[3,4,6,8,12],corpu:[],corpusbas:3,corpusdb:[3,4,6,7],corpussearch:[2,7,12,13],could:[3,4,7],count:12,creat:[4,12,13],creation:12,cumul:12,current:[3,6,7],dash:[7,8],dash_tag:7,dashtag:7,data:[3,8,12,13],databas:[4,7],dativ:8,decid:4,defin:[3,6,7],definit:12,delimit:2,depth:[4,7],describ:4,design:13,detail:[6,7,12],develop:[],devic:12,dic:9,dict:3,did:12,differ:[3,4],difficult:12,digit:8,direct:[7,12],directli:[6,7],directori:[6,12],disjunct:7,disjunctuion:7,disk:[6,12],dispatch:7,displai:12,dissemin:12,distanc:4,doc:[],docstr:7,document:[],doe:[4,7,12],dom:[4,7],domin:[4,7],done:4,doubli:3,download:12,dynam:12,each:[4,7],eas:12,easi:12,easier:12,easili:12,ecai:[0,12,13,14],ecosystem:13,edit:[3,13],editor:3,effect:12,effort:13,either:7,elimin:[4,12],elsewher:12,emac:2,embed:12,empti:7,enabl:12,encompass:7,encourag:12,end:[4,7],engin:[4,7,13],english:7,ensure_id:8,entir:7,entri:[4,8],environ:[12,13],equival:7,error:6,evalu:[4,7],even:[4,12],event:4,exact:7,exampl:[],except:[4,9],execut:12,exercis:12,exist:[7,12],expect:7,expens:6,explain:12,explicit:4,express:[3,7,12],expresss:[],extens:6,extension:12,extent:4,extract:12,facil:13,fair:12,fals:[6,7],fast:[7,13],featur:[12,13],fecth:3,fetch:6,fetch_al:6,few:4,field:7,file:[3,6,8,12],fileload:[6,12],filenam:6,filesystem:6,filter:3,find:[7,12],finish:12,first:[2,6,7,12],firstgrammar:12,fit:[7,12],fix:3,fledg:12,flestum:12,flexibl:4,follow:[7,8,12,13],foo:7,foobar:[],forest:12,form:2,format:[3,8,12],found:6,four:8,from:[2,3,4,6,7,8,12],frozenset:[],fulli:12,gain:12,gener:[2,6,7,8],genit:8,get:12,git:6,github:[6,7,12],githubload:[6,12],given:12,good:[3,7],group:12,hand:12,handl:[3,4,6],hash:6,hassl:6,have:[3,6,8,12],heavi:12,heavili:4,here:[3,12],high:4,histor:[3,6],homiliubok:12,host:12,how:6,howev:4,html:[],icecorpu:12,icepahc:[6,8,12],icepahc_cas:8,icepahc_case_label:8,icepahc_lemma:8,icepahc_word_split:8,icepahc_year:8,idea:7,ideal:4,idiosyncrat:8,idom:7,iff:7,ignor:7,ilovett:[],immedi:[6,7],immut:4,imper:7,implement:[3,4,6,7,12],impos:3,includ:[6,12],increas:4,inde:[7,12],indent:9,index:[],index_typ:10,individu:12,infinit:7,infrastructur:12,inherit:[3,6,7],initi:[6,7,13],input:12,insert:[3,4,9],insert_tre:4,insist:12,instal:12,instanc:[3,7],instead:4,instruct:12,integr:12,intent:7,interact:[12,13],interest:12,interfac:[3,4,5,6,7],interoper:2,interpret:7,invoc:7,ipython:[3,5],is_ec:10,is_leaf:10,is_nontermin:10,is_sil:10,is_text_leaf:10,is_trac:10,is_trace_str:10,isn:3,issu:[3,7],iter:[3,12],itself:12,jartein:12,javascript:13,jupyt:13,just:[3,12],kei:4,kind:[6,12],know:3,known:8,label:[4,7,8,9],label_and_index:10,lack:3,land:12,languag:[7,12,13],larg:12,latest:6,leaf:[4,9],learn:[12,13],leav:12,left:[4,7],left_sibl:9,level:[4,6],librari:[4,12],like:[3,7,12],limit:12,lin:12,line:2,linguist:12,link:[3,7],list:[3,4,6,12],load:[6,12],loader:[],local:6,locat:12,logic:12,look:7,lot:12,löndum:12,made:12,maintain:4,make:[4,6,12],manipul:13,manual:4,map:[3,8],mappingproxi:[],margur:12,massiv:7,master:6,mat:[7,12],match:7,match_tre:7,matching_tre:[3,4,7],matur:4,mayb:3,mean:[4,12],member:7,memori:6,metadata:[3,4,6,8,9],method:[3,4,6,7],middl:7,might:7,mind:13,mode:[2,7],model:12,modif:4,monoton:4,mood:7,more:[3,6,7,8,12],most:12,much:[6,12],multipl:3,multitudinari:12,mung:4,must:[3,6,7],mutabl:[3,4],mutablesequ:3,my_corpu:12,my_load:12,name:[6,7,8,9,12,13],nar:12,natur:7,necessari:4,need:[4,6,7,14],neg:7,negat:7,network:6,next:3,nice:3,node:[4,7],nomin:8,non:7,none:[3,4,6,9],nontermin:9,normal:4,note:[3,7],notebook:5,novic:12,npr:8,npx:7,number:3,obei:7,obj:9,object:[],obscur:12,old:7,onli:[4,6,7],open:7,oper:[2,4,7,8,12],optim:[4,7],order:[3,4,6],origin:7,other:[2,4,6,7,9,12],otherwis:7,out:12,output:12,over:3,overload:7,page:7,paramet:[2,3,4,6,7],parent:[4,7,9],parenthes:7,pars:[2,6,9,12],parseerror:9,parser:2,partak:6,partial:7,particular:12,pass:[4,6,12],path:6,pceec:8,pceec_metadata:8,penn:[3,6],perform:12,perhap:6,perspicu:12,pick:12,piec:[3,12],pipelin:6,pleas:7,pop:3,popul:6,possibl:[4,6,7],ppche:8,ppche_make_unicod:8,ppche_word_split:8,pre:6,preced:[4,7],precendec:4,prefix:7,present:[8,12],previou:3,primari:13,primarili:12,principl:4,privat:4,probabl:7,process:12,program:[12,13],programm:13,programmat:[3,4,7,12],project:[12,13],provid:[4,7,12,13],psd:[6,12],publicli:12,purpos:12,python:[4,7,12,13],queri:[],queryfunct:[4,7],question:3,quickli:12,rais:4,rather:[3,7,12],raw:4,read:[7,8],realli:3,reason:6,receiv:7,reconstitut:7,recurs:6,redund:12,ref:6,refer:[],reflect:4,reflex:4,regular:[4,7],rel:12,relationship:[4,12],relev:7,reli:4,relic:2,remov:[2,3,4],remove_index:10,repetit:12,replac:13,repo:[6,12],report:7,repositori:[6,12],repres:[3,4,7,8],represent:[7,13],request:6,requir:[7,12],research:12,resourc:[6,12],respons:4,restrict:7,result:3,revis:[6,12,13],revisit:4,right:[4,7],right_sibl:9,root:[4,9],roughli:7,rowid:4,rule:[7,12],run:[3,12],sag:12,same:4,save:3,sbj:7,schema:4,sci:12,search:[3,4,6,7,12],second:[2,7],secondari:13,section:12,see:[3,7],select:7,semant:3,sequenc:[3,4],sequenti:12,ser:12,set:[7,12],set_index:10,setja:12,sever:[7,12],sha1:6,share:12,shell:12,shorter:12,should:[3,4,6,7,12],sibl:4,significantli:4,similar:[3,7],simpl:12,sinc:[3,12],singl:[2,12],sister:4,skill:12,slog:12,slot:7,slow:7,slower:7,smart:3,softwar:2,some:[2,4],somehow:3,someon:12,someth:3,sometim:7,sourc:[2,3,4,5,6,7,8,9,10,12],special:7,specif:6,specifi:[6,7],speed:6,sprec:[4,7],sql:[4,7],sqlalchemi:[4,7],sqlite:4,standrad:6,statement:4,statist:12,store:4,str:[2,6,7],strategi:[4,12],string:[2,4,7,9,12],strip:2,strip_corpussearch_com:2,structur:[3,4,12],student:12,sturlunga:12,style:2,sub:3,subclass:6,successfulli:12,superclass:6,support:[6,7,8],system:[12,13],tabl:4,tag:[6,7,8],take:[2,4,7,12],target:[12,13],task:12,teach:13,technic:13,tens:7,term:12,tertiari:13,text:[3,4,9,12],than:[3,4,6,12],thei:12,themselv:[3,12],therein:[4,6],thi:[],thin:3,thing:12,think:12,thorlakur:12,through:[6,7,12],thu:[7,12],time:3,to_corpu:4,to_db:3,to_json:9,todo:[0,3,4,6,7,8,12],too:[6,7],tool:13,top:13,total:3,toward:7,trail:7,transfer:12,transform:[],tree:[],treebank:13,tricki:3,trigger:4,trunk:12,turn:7,two:[2,7,12],type:[2,4,6,7],typic:[7,12],understand:12,unexpect:7,unlik:[4,12],urtext:9,usabl:13,usag:[],user:[6,12,13],usernam:6,util:[],val:3,valid:4,valu:[4,8,9],varieti:[7,12],variou:8,vbpi:12,verb:7,veri:[7,12],version:[6,12],via:[6,7,13],visual:[12,13],wai:[6,7],walk:12,want:[3,12],weak:[],weakset:[],web:6,well:[3,6,12],what:[],when:3,where:[3,6,7],wherea:7,wherebi:3,whether:[3,6,7],which:[3,4,6,7,8,12],why:12,wide:12,window:3,within:3,without:[6,12],would:[3,4,7],wrap:[4,7],wrapperqueryfunct:7,writabl:3,write:3,write_penn_treebank:3,writem:0,written:[3,12,14],ycoe:8,ycoe_cas:8,year:8,yet:[4,7],yield:3,you:[3,6,7,12]},titles:["About Lovett","lovett package","lovett.compat module","lovett.corpus module","lovett.db module","lovett.ilovett module","lovett.loader module","lovett.query module","lovett.transform module","lovett.tree module","lovett.util module","lovett","Example usage","Lovett","Indexing"],titleterms:{about:0,compat:2,content:1,corpu:[3,12],develop:13,document:13,exampl:12,foobar:14,goal:13,ilovett:5,index:14,introduct:12,loader:[6,12],lovett:[0,1,2,3,4,5,6,7,8,9,10,11,12,13],modul:[1,2,3,4,5,6,7,8,9,10],nutshel:13,object:12,packag:1,queri:7,submodul:1,thi:13,transform:8,tree:9,usag:12,util:10,what:12}})