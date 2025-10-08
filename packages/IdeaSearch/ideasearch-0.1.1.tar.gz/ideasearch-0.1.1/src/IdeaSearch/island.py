import os
import json
import shutil
import gettext
import numpy as np
from datetime import datetime
from time import perf_counter
from math import isnan
from threading import Lock
from pathlib import Path
from typing import Tuple
from typing import Callable
from typing import Optional
from typing import List
from copy import deepcopy
from os.path import basename
from os.path import sep as seperator
from pywheels.file_tools import append_to_file
from pywheels.file_tools import guarantee_file_exist
from IdeaSearch.utils import get_label
from IdeaSearch.utils import make_boltzmann_choice


# 国际化设置
_LOCALE_DIR = Path(__file__).parent / "locales"
_DOMAIN = "ideasearch"
gettext.bindtextdomain(_DOMAIN, _LOCALE_DIR)
gettext.textdomain(_DOMAIN)

__all__ = [
    "Idea",
    "Island",
]


class Idea:
    
    def __init__(
        self, 
        path: str,
        evaluate_func: Optional[Callable[[str], Tuple[float, Optional[str]]]], 
        level: int,
        content: Optional[str] = None,
        raw_response: Optional[str] = None,
        score: Optional[float] = None, 
        info: Optional[str] = None,
        source: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        
        self.path = str(path)
        self.source = source
        self.level = level
        self.raw_response = raw_response
        
        if created_at is not None:
            self.created_at = created_at
        else:        
            self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if evaluate_func is not None:
            with open(path, 'r', encoding = "UTF-8") as file:
                self.content = file.read()
            self.score, self.info = evaluate_func(self.content)
        else:
            self.content = content
            self.score = score
            self.info = info


class Island:

    # ----------------------------- 岛屿初始化 ----------------------------- 

    def __init__(
        self,
        ideasearcher,
        island_id: int,
        default_similarity_distance_func: Callable[[str, str], float],
        console_lock: Lock,
    )-> None:
        
        self.ideasearcher = ideasearcher
        self.id = island_id
        self.ideas = []
        self.idea_similar_nums = []
        
        # 获取国际化函数
        self._ = ideasearcher._
        
        database_path = self.ideasearcher.get_database_path()
        assert database_path is not None
        
        self.path = f"{database_path}{seperator}ideas{seperator}island{self.id}"
        guarantee_file_exist(
            file_path = self.path,
            is_directory = True,
        )

        self.interaction_count = 0
        self.interaction_num = 0
        
        self._lock = Lock()
        self._console_lock = console_lock
        
        self.default_similarity_distance_func = default_similarity_distance_func
        self.random_generator = np.random.default_rng()
        
        self._best_score = -np.inf
        self._best_idea = None
        
        self._reset_ideas()
        self._status = "Running"
    
    # ----------------------------- 外部调用动作 ----------------------------- 
        
    def load_ideas_from(
        self,
        folder_name: str,
    ):
        
        with self._lock:
        
            database_path = self.ideasearcher.get_database_path()
            diary_path = self.ideasearcher.get_diary_path()
            load_idea_skip_evaluation = self.ideasearcher.get_load_idea_skip_evaluation()
            initialization_cleanse_threshold = self.ideasearcher.get_initialization_cleanse_threshold()
            delete_when_initial_cleanse = self.ideasearcher.get_delete_when_initial_cleanse()
            evaluate_func = self.ideasearcher.get_evaluate_func()
            assert database_path is not None
            
            idea_source_path = f"{database_path}{seperator}ideas{seperator}{folder_name}"
            idea_source_path_ideas = []
            idea_source_score_sheet_path = f"{idea_source_path}{seperator}score_sheet_{folder_name}.json"
            idea_source_score_sheet: Optional[dict] = None
            
            if load_idea_skip_evaluation:
                
                try:
                    with open(
                        file = idea_source_score_sheet_path, 
                        mode = "r", 
                        encoding = "UTF-8"
                    ) as file:
                        idea_source_score_sheet = json.load(file)
                        
                    with self._console_lock:
                        append_to_file(
                            file_path=diary_path,
                            content=self._("【%d号岛屿】 已从 %s 成功读取用于迅捷加载的 score sheet 文件！") % (self.id, idea_source_score_sheet_path),
                        )
                        
                except Exception as error:
                    
                    idea_source_score_sheet = {}
                    
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 未从 %s 成功读取用于迅捷加载的 score sheet 文件，报错：\n%s\n请检查该行为是否符合预期！") % (self.id, idea_source_score_sheet_path, error),
                        )
                        
            
            self._reset_ideas()
            
            # 此部分疑似存在 mac OS 系统的兼容性问题
            initial_source = self._("初始化时读入")
            path_to_search = Path(idea_source_path).resolve()
            
            for path in path_to_search.rglob('*.idea'):
                
                if not os.path.isfile(path): continue
                    
                idea: Optional[Idea] = None
                
                if load_idea_skip_evaluation:
                    
                    assert idea_source_score_sheet is not None
                    
                    if basename(path) in idea_source_score_sheet:
                        
                        with open(
                            file = path, 
                            mode = "r", 
                            encoding = "UTF-8"
                        ) as file:
                            content = file.read()
                            
                        recorded_item = idea_source_score_sheet[basename(path)]
                            
                        score = recorded_item["score"]
                        info = recorded_item["info"]
                        source = recorded_item["source"]
                        level = recorded_item["level"]
                        created_at = recorded_item["created_at"]
                        raw_response = recorded_item.get("raw_response", "")
                        
                        if info == "": info = None
                            
                        idea = Idea(
                            path = str(path),
                            level = level,
                            evaluate_func = None,
                            content = content,
                            score = score,
                            raw_response = raw_response,
                            info = info,
                            source = source, 
                            created_at = created_at,
                        )
                        
                        if info is not None:
                            with self._console_lock:
                                append_to_file(
                                    file_path=diary_path,
                                    content=self._("【%d号岛屿】 已从 score sheet 文件中迅捷加载文件 %s 的评分与评语！") % (self.id, basename(path)),
                                )
                        else:
                            with self._console_lock:
                                append_to_file(
                                    file_path=diary_path,
                                    content=self._("【%d号岛屿】 已从 score sheet 文件中迅捷加载文件 %s 的评分！") % (self.id, basename(path)),
                                )
                        
                    else:
                        with self._console_lock:
                            append_to_file(
                                file_path=diary_path,
                                content=self._("【%d号岛屿】 没有在 score sheet 文件中找到文件 %s ，迅捷加载失败！") % (self.id, basename(path)),
                            )
                        
                        idea = Idea(
                            level = 0,
                            path = str(path),
                            evaluate_func = evaluate_func,
                            source = initial_source,
                        )
                    
                else:
                    idea = Idea(
                        level = 0,
                        path = str(path),
                        evaluate_func = evaluate_func,
                        source = initial_source,
                    )
                
                assert idea.score is not None
                
                if idea.score < initialization_cleanse_threshold:
                    
                    if delete_when_initial_cleanse:
                        path.unlink()
                        with self._console_lock:
                            append_to_file(
                                file_path=diary_path,
                                content=self._("【%d号岛屿】 文件 %s 评分未达到%.2f，已删除。") % (self.id, basename(path), initialization_cleanse_threshold),
                            )
                            
                    else:
                        idea_source_path_ideas.append(idea)
                        self.ideasearcher.record_ideas_in_backup([idea])
                        with self._console_lock:
                            append_to_file(
                                file_path=diary_path,
                                content=self._("【%d号岛屿】 文件 %s 评分未达到%.2f，已忽略。") % (self.id, basename(path), initialization_cleanse_threshold),
                            )
                            
                else:
                    idea_source_path_ideas.append(idea)
                    self.ideasearcher.record_ideas_in_backup([idea])
                    self.ideas.append(idea)
                    with self._console_lock:
                        append_to_file(
                            file_path=diary_path,
                            content=self._("【%d号岛屿】 初始文件 %s 已评分并加入%d号岛屿。") % (self.id, basename(path), self.id),
                        )
                    shutil.copy2(
                        src = f"{idea_source_path}{seperator}{basename(path)}",
                        dst = f"{self.path}{seperator}{basename(path)}",
                    )
                
            new_score_sheet = {
                basename(idea.path): {
                    "score": idea.score,
                    "info": idea.info if idea.info is not None else "",
                    "raw_response": idea.raw_response if idea.raw_response is not None else "",
                    "source": idea.source,
                    "level": idea.level,
                    "created_at": idea.created_at,
                }
                for idea in idea_source_path_ideas
            }

            with open(
                file = idea_source_score_sheet_path, 
                mode = "w", 
                encoding = "UTF-8",
            ) as file_pointer:
                
                json.dump(
                    new_score_sheet, 
                    file_pointer, 
                    ensure_ascii = False,
                    indent = 4,
                )         
            self._sync_score_sheet()
            self._sync_best_score()
            self._sync_similar_num_list()
            
            
    def link_samplers(
        self,
        samplers
    )-> None:
        
        with self._lock:
        
            self.samplers = samplers

        
    def fuel(
        self,
        additional_interaction_num: int,
    )-> None:
        
        with self._lock:
            
            if additional_interaction_num <= 0:
                raise RuntimeError(self._("【%d号岛屿】 fuel 动作的参数 `additional_interaction_num` 应为一正整数，不应为%d！") % (self.id, additional_interaction_num))
            
            self.interaction_num += additional_interaction_num
            self._status = "Running"


    def get_status(
        self,
    )-> str:
        
        with self._lock:
            
            if self.ideasearcher._get_best_score() >= self.ideasearcher.get_shutdown_score():
                self._status = "Terminated"
                
            return self._status
        
    
    def get_examples(
        self,
    )-> Optional[list[Tuple]]:
        
        with self._lock:
            
            if self._status == "Terminated":
                return None
            
            diary_path = self.ideasearcher.get_diary_path()
            mutation_func = self.ideasearcher.get_mutation_func()
            mutation_interval = self.ideasearcher.get_mutation_interval()
            crossover_func = self.ideasearcher.get_crossover_func()
            crossover_interval = self.ideasearcher.get_crossover_interval()
            similarity_sys_info_thresholds = self.ideasearcher.get_similarity_sys_info_thresholds()
            similarity_sys_info_prompts = self.ideasearcher.get_similarity_sys_info_prompts()
            sample_temperature = self.ideasearcher.get_sample_temperature()
            generation_bonus = self.ideasearcher.get_generation_bonus()
            
            self.interaction_count += 1
            
            with self._console_lock:
                    append_to_file(
                        file_path = diary_path,
                        content = self._("【%d号岛屿】 已分发交互次数为： %d ，还剩 %d 次！") % (self.id, self.interaction_count, self.interaction_num-self.interaction_count),
                    )
            
            if mutation_func is not None:
                
                assert mutation_interval is not None
                
                if self.interaction_count % mutation_interval == 0:
                    self._mutate()
            
            if crossover_func is not None:
                
                assert crossover_interval is not None
                
                if self.interaction_count % crossover_interval == 0:
                    self._crossover()
            
            self._check_threshold()
            
            if len(self.ideas) == 0:
                with self._console_lock:
                    append_to_file(
                        file_path = diary_path,
                        content = self._("【%d号岛屿】 发生异常： ideas 列表为空！") % self.id,
                    )
                exit()
            
            selected_indices = make_boltzmann_choice(
                energies = np.array([idea.score for idea in self.ideas]) + generation_bonus * np.array([idea.level for idea in self.ideas]),
                temperature = sample_temperature,
                size = min(len(self.ideas), self.ideasearcher.get_examples_num()),
                replace = False,
            )
            assert not isinstance(selected_indices, int)
            
            selected_examples = []
            for i in selected_indices:
                selected_index = int(i)
                example_idea = self.ideas[selected_index]
                
                if similarity_sys_info_thresholds is not None:
                    
                    assert similarity_sys_info_prompts is not None
                    
                    similar_num = self.idea_similar_nums[selected_index]
                    similarity_prompt = get_label(
                        x = similar_num,
                        thresholds = similarity_sys_info_thresholds,
                        labels = similarity_sys_info_prompts
                    )
                else:
                    similar_num = None
                    similarity_prompt = None
                    
                selected_examples.append((
                    example_idea.content,
                    example_idea.score,
                    example_idea.info,
                    similar_num,
                    similarity_prompt,
                    example_idea.path,
                    example_idea.level,
                ))

            return selected_examples
    
    
    def get_ideas_called_when_generate_prompt_func_set(
        self,
    ):
        with self._lock:
            
            if self._status == "Terminated":
                return None
            
            diary_path = self.ideasearcher.get_diary_path()
            
            self.interaction_count += 1
            
            with self._console_lock:
                append_to_file(
                    file_path = diary_path,
                    content = (
                        self._("【%d号岛屿】 已分发交互次数为： %d ，\n 还剩 %d 次！") %
                        (self.id, self.interaction_count, self.interaction_num-self.interaction_count)
                    )
                )
                
            self._check_threshold()
                
            return deepcopy(self.ideas)
        
        
    def receive_result(
        self, 
        result: List[Tuple[str, str, float, str]], 
        evaluator_id: int,
        source: str,
        level: int,
    )-> None:
        
        with self._lock:
            
            if not result:
                
                self.ideasearcher.assess_database()
                return
            
            diary_path = self.ideasearcher.get_diary_path()
    
            for raw_response, idea_content, score, info in result:
                
                self._store_idea(
                    raw_response = raw_response,
                    idea = idea_content,
                    level = level,
                    score = score,
                    info = info,
                    source = source,
                )
                
            with self._console_lock:    
                append_to_file(
                    file_path = diary_path,
                    content = self._("【%d号岛屿】 %d 号评估器递交的 %d 个新文件已评分并加入%d号岛屿。") % (self.id, evaluator_id, len(result), self.id),
                )
            
            self._sync_score_sheet()
            self._sync_best_score()
            self._sync_similar_num_list()
            
            self.ideasearcher.assess_database()
            
            
    def accept_colonization(
        self,
        foreign_ideas: List[Idea],
    )-> None:
        
        with self._lock:
            
            self._reset_ideas()
            self.ideas = foreign_ideas
            
            for idea in foreign_ideas:
                assert idea.content is not None
                with open(
                    file = f"{self.path}{seperator}{basename(idea.path)}",
                    mode = "w",
                    encoding = "UTF-8",
                ) as file:
                    file.write(idea.content)
                    
            self._sync_best_score()
            self._sync_score_sheet()
            self._sync_similar_num_list()
            
            
    # ----------------------------- 内部调用动作 -----------------------------     
    
    def _reset_ideas(
        self
    )-> None:
        
        self.ideas = []
        self.idea_similar_nums = []  
        
        shutil.rmtree(self.path)
        guarantee_file_exist(
            file_path = self.path,
            is_directory = True,
        )    
            
            
    def _sync_score_sheet(self):
        
        diary_path = self.ideasearcher.get_diary_path()
        program_name = self.ideasearcher.get_program_name()
        
        score_sheet_path = f"{self.path}{seperator}score_sheet_island{self.id}.json"
        
        start_time = perf_counter()
        
        score_sheet = {
            basename(idea.path): {
                "score": idea.score,
                "info": idea.info if idea.info is not None else "",
                "source": idea.source,
                "level": idea.level,
                "created_at": idea.created_at,
            }
            for idea in self.ideas
        }

        with open(
            file = score_sheet_path, 
            mode = "w", 
            encoding = "UTF-8",
        ) as file:
            
            json.dump(
                obj = score_sheet, 
                fp = file, 
                ensure_ascii = False,
                indent = 4
            )
            
        end_time = perf_counter()
        total_time = end_time - start_time
        
        with self._console_lock:
            append_to_file(
                file_path = diary_path,
                content = self._("【%d号岛屿】 %s 的 score sheet 已更新，用时%.2f秒！") % (self.id, program_name, total_time),
            )
            
    def _sync_best_score(self):
            
        for idea in self.ideas:
            assert idea.score is not None
            if idea.score > self._best_score:
                self._best_score = idea.score
                self._best_idea = idea
            
            
    def _sync_similar_num_list(self):
        
        diary_path = self.ideasearcher.get_diary_path()
        similarity_distance_func = self.ideasearcher.get_similarity_distance_func()
        similarity_threshold = self.ideasearcher.get_similarity_threshold()
        assert similarity_distance_func is not None
        
        
        start_time = perf_counter()
        
        
        self.idea_similar_nums = []
        
        if similarity_distance_func == self.default_similarity_distance_func:

            scores = np.array([idea.score for idea in self.ideas])
            diff_matrix = np.abs(scores[:, None] - scores[None, :])

            for i, idea_i in enumerate(self.ideas):
                score_similar_indices = set(np.where(diff_matrix[i] <= similarity_threshold)[0])
                content_equal_indices = set(
                    j for j, idea_j in enumerate(self.ideas)
                    if idea_j.content == idea_i.content
                )
                total_similar_indices = score_similar_indices | content_equal_indices

                self.idea_similar_nums.append(len(total_similar_indices))
            
        else:
            for i, idea_i in enumerate(self.ideas):
                
                similar_count = 0
                
                for j, idea_j in enumerate(self.ideas):
                    
                    if i == j or idea_i.content == idea_j.content:
                        similar_count += 1
                        continue
                    
                    assert idea_i.content is not None
                    assert idea_j.content is not None
                        
                    score_diff = similarity_distance_func(idea_i.content, idea_j.content) 
                    if score_diff <= similarity_threshold: similar_count += 1
                        
                self.idea_similar_nums.append(similar_count)
            
        end_time = perf_counter()
        total_time = end_time - start_time
            
        with self._console_lock:
            append_to_file(
                file_path = diary_path,
                content = self._("【%d号岛屿】 成功将idea_similar_nums与ideas同步，用时%.2f秒！") % (self.id, total_time),
            )
    
    
    def _check_threshold(self):
        diary_path = self.ideasearcher.get_diary_path()
        if self.interaction_count >= self.interaction_num:
            with self._console_lock:
                append_to_file(
                    file_path = diary_path,
                    content = self._("【%d号岛屿】 采样次数已分发完毕，IdeaSearch将在各采样器完成手头任务后结束。") % self.id,
                )
            self._status = "Terminated"

    
    def _mutate(self)-> None:
        
        diary_path = self.ideasearcher.get_diary_path()
        program_name = self.ideasearcher.get_program_name()
        evaluate_func = self.ideasearcher.get_evaluate_func()
        handover_threshold = self.ideasearcher.get_hand_over_threshold()
        mutation_num = self.ideasearcher.get_mutation_num()
        mutation_temperature = self.ideasearcher.get_mutation_temperature()
        mutation_func = self.ideasearcher.get_mutation_func()
        generation_bonus = self.ideasearcher.get_generation_bonus()
        assert evaluate_func is not None
        assert mutation_num is not None
        assert mutation_temperature is not None
        assert mutation_func is not None
        assert generation_bonus is not None
        
        with self._console_lock:
            append_to_file(
                file_path = diary_path,
                content = self._("【%d号岛屿】 现在开始进行单体突变！") % self.id,
            )
        
        for index in range(mutation_num):
            
            selected_index = make_boltzmann_choice(
                energies = np.array([idea.score for idea in self.ideas]) + generation_bonus * np.array([idea.level for idea in self.ideas]),
                temperature = mutation_temperature,
            )
            assert isinstance(selected_index, int)
            
            selected_idea = self.ideas[selected_index]
            
            try:
                assert selected_idea.content is not None
                mutated_idea = mutation_func(selected_idea.content)
                if not isinstance(mutated_idea, str):
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 调用 %s 的单体突变函数时发生错误：返回结果中的 mutated_idea 应为一字符串，不应为一个 %s 类型的对象！\n此轮单体突变意外终止！") % (self.id, program_name, type(mutated_idea)),
                        )
                    return
            except Exception as error:
                with self._console_lock:
                    append_to_file(
                        file_path = diary_path,
                        content = self._("【%d号岛屿】 第 %d 次单体突变在运行 mutation_func 时发生了错误：\n%s\n此轮单体突变意外终止！") % (self.id, index+1, error),
                    )
                return
            
            try:
                score, info = evaluate_func(mutated_idea)
                
                if not isinstance(score, float):
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 调用 %s 的评估函数时发生错误：返回结果中的 score 应为一浮点数，不应为一个 %s 类型的对象！\n此轮单体突变意外终止！") % (self.id, program_name, type(score)),
                        )
                    return
                
                if isnan(score):
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 调用 %s 的评估函数时发生错误：返回结果中的 score 不应为 NaN ！\n此轮单体突变意外终止！") % (self.id, program_name),
                        )
                    return
                
                if info is not None:
                    if not isinstance(info, str):
                        with self._console_lock:
                            append_to_file(
                                file_path = diary_path,
                                content = self._("【%d号岛屿】 调用 %s 的评估函数时发生错误：返回结果中的 info 应为 None 或一字符串，不应为一个 %s 类型的对象！\n此轮单体突变意外终止！") % (self.id, program_name, type(info)),
                            )
                        return
                
            except Exception as error:
                with self._console_lock:
                    append_to_file(
                        file_path = diary_path,
                        content = self._("【%d号岛屿】 调用 %s 的评估函数时发生错误：\n%s\n此轮单体突变意外终止！") % (self.id, program_name, error),
                    )  
                return
            
            source = self._("由 %s(%.2f) 突变而来") % (basename(selected_idea.path), selected_idea.score)
            
            if score >= handover_threshold:
            
                path = self._store_idea(
                    idea = mutated_idea,
                    score = score,
                    info = info, 
                    source = source,
                    raw_response = "",
                    level = selected_idea.level + 1,
                )
                
                if path is not None:
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 第 %d 次单体突变： %s 突变为 %s ") % (self.id, index+1, basename(selected_idea.path), basename(path)),
                        )
                    self._sync_score_sheet()
                    self._sync_best_score()
                    self._sync_similar_num_list()
                else:
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 第 %d 次单体突变发生了错误：\n%s\n此轮单体突变意外终止！") % (self.id, index+1, self._store_idea_error_message),
                        )
                    return
                
            else:
                with self._console_lock:
                    append_to_file(
                        file_path = diary_path,
                        content = self._("【%d号岛屿】 第 %d 次单体突变结果未达到入库分数阈值（%.2f分），已删除！") % (self.id, index+1, handover_threshold),
                    )
                
        with self._console_lock:
            append_to_file(
                file_path = diary_path,
                content = self._("【%d号岛屿】 此轮单体突变已结束。") % self.id,
            )
    
    
    def _crossover(self) -> None:
        
        diary_path = self.ideasearcher.get_diary_path()
        program_name = self.ideasearcher.get_program_name()
        evaluate_func = self.ideasearcher.get_evaluate_func()
        handover_threshold = self.ideasearcher.get_hand_over_threshold()
        crossover_num = self.ideasearcher.get_crossover_num()
        crossover_temperature = self.ideasearcher.get_crossover_temperature()
        crossover_func = self.ideasearcher.get_crossover_func()
        generation_bonus = self.ideasearcher.get_generation_bonus()
        assert evaluate_func is not None
        assert crossover_num is not None
        assert crossover_temperature is not None
        assert crossover_func is not None
        assert generation_bonus is not None
    
        with self._console_lock:
            diary_path = self.ideasearcher.get_diary_path()
            append_to_file(
                file_path = diary_path,
                content = self._("【%d号岛屿】 现在开始进行交叉变异！") % self.id,
            )

        for index in range(crossover_num):
            
            parent_indices = make_boltzmann_choice(
                energies = np.array([idea.score for idea in self.ideas]) + generation_bonus * np.array([idea.level for idea in self.ideas]),
                temperature = crossover_temperature,
                size = 2,
                replace = False,
            )
            assert not isinstance(parent_indices, int)
            
            parent_1 = self.ideas[parent_indices[0]]
            parent_2 = self.ideas[parent_indices[1]]

            try:
                crossover_idea = crossover_func(
                    parent_1.content, parent_2.content
                )
                if not isinstance(crossover_idea, str):
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 调用 %s 的交叉变异函数时发生错误：返回结果中的 crossover_idea 应为一字符串，不应为一个 %s 类型的对象！\n此轮交叉变异意外终止！") % (self.id, program_name, type(crossover_idea)),
                        )
                    return
            except Exception as error:
                with self._console_lock:
                    append_to_file(
                        file_path = diary_path,
                        content = self._("【%d号岛屿】 第 %d 次交叉变异在运行 crossover_func 时发生了错误：\n%s") % (self.id, index+1, error),
                    )
                continue
            
            try:
                score, info = evaluate_func(crossover_idea)
                
                if not isinstance(score, float):
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 调用 %s 的评估函数时发生错误：返回结果中的 score 应为一浮点数，不应为一个 %s 类型的对象！\n此轮交叉变异意外终止！") % (self.id, program_name, type(score)),
                        )
                    return
                
                if isnan(score):
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 调用 %s 的评估函数时发生错误：返回结果中的 score 不应为 NaN ！\n此轮交叉变异意外终止！") % (self.id, program_name),
                        )
                    return
                
                if info is not None:
                    if not isinstance(info, str):
                        with self._console_lock:
                            append_to_file(
                                file_path = diary_path,
                                content = self._("【%d号岛屿】 调用 %s 的评估函数时发生错误：返回结果中的 info 应为 None 或一字符串，不应为一个 %s 类型的对象！\n此轮交叉变异意外终止！") % (self.id, program_name, type(info)),
                            )
                        return
                
            except Exception as error:
                with self._console_lock:
                    append_to_file(
                        file_path = diary_path,
                        content = self._("【%d号岛屿】 调用 %s 的评估函数时发生错误：\n%s\n此轮交叉变异意外终止！") % (self.id, program_name, error),
                    )  
                return
            
            source = self._("由 %s(%.2f) 和 %s(%.2f) 交叉而来") % (basename(parent_1.path), parent_1.score, basename(parent_2.path), parent_2.score)

            if score >= handover_threshold:
                
                path = self._store_idea(
                    idea = crossover_idea,
                    score = score,
                    info = info,
                    source = source,
                    raw_response = "",
                    level = max(parent_1.level, parent_2.level) + 1,
                )

                if path is not None:
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 第 %d 次交叉变异：%s × %s 交叉为 %s ") % (self.id, index+1, basename(parent_1.path), basename(parent_2.path), basename(path)),
                        )
                    self._sync_score_sheet()
                    self._sync_best_score()
                    self._sync_similar_num_list()
                else:
                    with self._console_lock:
                        append_to_file(
                            file_path = diary_path,
                            content = self._("【%d号岛屿】 第 %d 次交叉变异发生了错误：\n%s\n此轮交叉变异意外终止！") % (self.id, index+1, self._store_idea_error_message),
                        )
                    return
                
            else:
                with self._console_lock:
                    append_to_file(
                        file_path = diary_path,
                        content = self._("【%d号岛屿】 第 %d 次交叉变异结果未达到入库分数阈值（%.2f分），已删除！") % (self.id, index+1, handover_threshold),
                    )

        with self._console_lock:
            append_to_file(
                file_path = diary_path,
                content = self._("【%d号岛屿】 此轮交叉变异已结束。") % self.id,
            )
    
    
    def _store_idea(
        self, 
        raw_response: str,
        idea: str,
        level: int,
        evaluate_func: Optional[Callable[[str], Tuple[float, Optional[str]]]] = None,
        score: Optional[float] = None,
        info: Optional[str] = None,
        source: Optional[str] = None,
    )-> Optional[str]:
        
        """
        将一个新的 idea 内容保存为文件，并添加到内部 idea 列表中。
        为了避免重复运行 evaluate_func 带来的时间开销，允许调用者在以下两个情形间选择：
        
        1. evaluate_func is None （已在外部评估 idea ）
        这时应该传入 score 和 info
        
        2. evaluate_func is not None （尚未评估 idea ）
        这时可以不传入 score 和 info

        Args:
            idea (str): 需要存储的 idea 内容（字符串格式）。
            evaluate_func (Optional[Callable[[str, str], float]]): 用于评价 idea 的函数。
            score (Optional[float]): 预设的 idea 评分。
            info (Optional[str]): 与 idea 相关的附加信息。
            source (Optional[str]): idea 的来源。

        Returns:
            Optional[str]: 成功则返回该 idea 对应的文件路径；若出错则返回 None。
        """
        
        try:
            path = self._get_new_idea_path()
            
            with open(path, 'w', encoding='utf-8') as file:
                file.write(idea)
                
            new_idea = Idea(
                path = path,
                level = level,
                evaluate_func = evaluate_func,
                content = idea,
                raw_response = raw_response,
                score = score,
                info = info,
                source = source,
            )

            self.ideas.append(new_idea)
            self.ideasearcher.record_ideas_in_backup([new_idea])

            return path

        except Exception as error:
            self._store_idea_error_message = error
            return None
            
            
    def _get_new_idea_path(
        self,
    )-> str:
        
        idea_uid = self.ideasearcher.get_idea_uid()
        path = os.path.join(f"{self.path}", f"idea_{idea_uid}.idea")
        return path
