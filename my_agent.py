from agt_server.agents.base_agents.lsvm_agent import MyLSVMAgent
from agt_server.local_games.lsvm_arena import LSVMArena
from agt_server.agents.test_agents.lsvm.min_bidder.my_agent import MinBidAgent
from agt_server.agents.test_agents.lsvm.jump_bidder.jump_bidder import JumpBidder
from agt_server.agents.test_agents.lsvm.truthful_bidder.my_agent import TruthfulBidder
import time
import os
import random
import gzip
import json
from path_utils import path_from_local_root


NAME = "singleton"# TODO: Please give your agent a NAME

class MyAgent(MyLSVMAgent):
    def setup(self):
        #TODO: Fill out with anything you want to initialize each auction
        self.debug = False

    def good_is_3_away(self, good, good_indices):
        ROW_LENGTH = 6
        row, col = good_indices[good]


        regional_good = self.get_regional_good()
        if regional_good:
            center_row, center_col = good_indices[self.get_regional_good()]
            return (abs(col - center_col) + abs(row - center_row)) <= 3
        else:
            return True


    def initial_bid(self) -> dict:
        bids = {}
        for good in self.get_goods():
            if not self.good_is_3_away(good, self.get_goods_to_index()):
                continue
            self_valuation = self.get_valuation(good)
            if self.get_current_prices_map() and self_valuation < self.get_current_prices_map()[good]:
                continue
            tentative_price = max(self.get_min_bids()[good], self_valuation)
            bids[good] = tentative_price
        if not self.is_valid_bid_bundle(bids) and self.debug:
            print(("regional" if self.get_regional_good() else "national"), ", bids: ", bids)
            print("Detected invalid bundle")
            exit(0)
        return bids


    def national_bidder_strategy(self): 
        # TODO: Fill out with your national bidder strategy
        min_bids = self.get_min_bids()
        valuations = self.get_valuations() 
        if len(self.get_tentative_allocation()) == 0:
            return self.initial_bid()

        bids = {} 
        current_valuation = self.calc_total_valuation(self.get_tentative_allocation())
        working_bundle = self.get_tentative_allocation().copy()
        for good in self.get_goods():
            if good in self.get_tentative_allocation():
                continue
            working_bundle.add(good)
            new_valuation = self.calc_total_valuation(working_bundle)
            working_bundle.remove(good)
            valuation_added = new_valuation - current_valuation
            if valuation_added > self.get_min_bids()[good]:
                bids[good] = self.get_min_bids()[good]
        
        if not self.is_valid_bid_bundle(bids) and self.debug:
            print("Detected invalid bundle")
            exit(0)

        return bids

    def regional_bidder_strategy(self): 
        # TODO: Fill out with your regional bidder strategy
        min_bids = self.get_min_bids()
        valuations = self.get_valuations() 
        if len(self.get_tentative_allocation()) == 0:
            return self.initial_bid()
        
        bids = {} 
        current_valuation = self.calc_total_valuation(self.get_tentative_allocation())
        working_bundle = self.get_tentative_allocation().copy()
        for good in self.get_goods():
            if good in self.get_tentative_allocation():
                continue
            working_bundle.add(good)
            new_valuation = self.calc_total_valuation(working_bundle)
            working_bundle.remove(good)
            valuation_added = new_valuation - current_valuation
            if valuation_added > self.get_min_bids()[good]:
                bids[good] = self.get_min_bids()[good]

        if not self.is_valid_bid_bundle(bids) and self.debug:
            print("Detected invalid bundle")
            exit(0)

        return bids

    def get_bids(self):
        if self.is_national_bidder(): 
            return self.national_bidder_strategy()
        else: 
            return self.regional_bidder_strategy()
    
    def update(self):
        #TODO: Fill out with anything you want to update each round
        pass 

    def teardown(self):
        #TODO: Fill out with anything you want to run at the end of each auction
        pass 

################### SUBMISSION #####################
my_agent_submission = MyAgent(NAME)
####################################################


def process_saved_game(filepath): 
    """ 
    Here is some example code to load in a saved game in the format of a json.gz and to work with it
    """
    print(f"Processing: {filepath}")
    
    # NOTE: Data is a dictionary mapping 
    with gzip.open(filepath, 'rt', encoding='UTF-8') as f:
        game_data = json.load(f)
        for agent, agent_data in game_data.items(): 
            if agent_data['valuations'] is not None: 
                # agent is the name of the agent whose data is being processed 
                agent = agent 
                
                # bid_history is the bidding history of the agent as a list of maps from good to bid
                bid_history = agent_data['bid_history']
                
                # price_history is the price history of the agent as a list of maps from good to price
                price_history = agent_data['price_history']
                
                # util_history is the history of the agent's previous utilities 
                util_history = agent_data['util_history']
                
                # util_history is the history of the previous tentative winners of all goods as a list of maps from good to winner
                winner_history = agent_data['winner_history']
                
                # elo is the agent's elo as a string
                elo = agent_data['elo']
                
                # is_national_bidder is a boolean indicating whether or not the agent is a national bidder in this game 
                is_national_bidder = agent_data['is_national_bidder']
                
                # valuations is the valuations the agent recieved for each good as a map from good to valuation
                valuations = agent_data['valuations']
                
                # regional_good is the regional good assigned to the agent 
                # This is None in the case that the bidder is a national bidder 
                regional_good = agent_data['regional_good']
            
            # TODO: If you are planning on learning from previously saved games enter your code below. 
            
            
        
def process_saved_dir(dirpath): 
    """ 
     Here is some example code to load in all saved game in the format of a json.gz in a directory and to work with it
    """
    for filename in os.listdir(dirpath):
        if filename.endswith('.json.gz'):
            filepath = os.path.join(dirpath, filename)
            process_saved_game(filepath)
            

if __name__ == "__main__":
    
    # Heres an example of how to process a singular file 
    # process_saved_game(path_from_local_root("saved_games/2024-04-08_17-36-34.json.gz"))
    # or every file in a directory 
    # process_saved_dir(path_from_local_root("saved_games"))
    
    ### DO NOT TOUCH THIS #####
    agent = MyAgent(NAME)
    arena = LSVMArena(
        num_cycles_per_player = 3,
        timeout=1,
        local_save_path="saved_games",
        players=[
            agent,
            MyAgent("CP - MyAgent"),
            MyAgent("CP2 - MyAgent"),
            MyAgent("CP3 - MyAgent"),
            MinBidAgent("Min Bidder"), 
            JumpBidder("Jump Bidder"), 
            TruthfulBidder("Truthful Bidder"), 
        ]
    )
    
    start = time.time()
    arena.run()
    end = time.time()
    print(f"{end - start} Seconds Elapsed")
