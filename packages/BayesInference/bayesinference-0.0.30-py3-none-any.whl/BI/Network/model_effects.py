from BI.Network.util import array_manip
import jax 
from jax import jit
import jax.numpy as jnp
from numpyro import deterministic
import os
import sys
import inspect
from BI.Utils.np_dists_old import UnifiedDist as dist
from functools import partial
class Neteffect(array_manip):
    def __init__(self) -> None:
        pass

    @staticmethod 
    @jit
    def logit(x):
        """
        Computes the logit transformation.

        Parameters
        ----------
        x : float or array-like
            Input value(s) in the range (0, 1).

        Returns
        -------
        float or array-like
            The logit-transformed value(s): log(x / (1 - x)).
        """
        return jnp.log(x / (1 - x))

    # Sender receiver  ----------------------
    @staticmethod 
    def nodes_random_effects(N_id, sr_mu = 0, sr_sd = 1, sr_sigma_rate = 1, cholesky_dim = 2, cholesky_density = 2, sample = False, diag = False ):
        sr_raw =  dist.normal(sr_mu, sr_sd, shape=(2, N_id), name = 'sr_raw', sample = sample)
        sr_sigma =  dist.exponential( sr_sigma_rate, shape= (2,), name = 'sr_sigma', sample = sample)
        sr_L = dist.lkj_cholesky(cholesky_dim, cholesky_density, name = "sr_L", sample = sample)
        rf = deterministic('sr_rf',(((sr_L @ sr_raw).T * sr_sigma)))

        if diag:
            print("sr_raw--------------------------------------------------------------------------------")
            print(sr_raw)
            print("sr_sigma--------------------------------------------------------------------------------")
            print(sr_sigma)
            print("sr_L--------------------------------------------------------------------------------")
            print(sr_L)
            print("rf--------------------------------------------------------------------------------")
            print(rf)
        return rf, sr_raw, sr_sigma, sr_L
   
    def nodes_terms(sender_predictors, receiver_predictors,
                    N_var_sender = 1, N_var_receiver = 1,
                    s_mu = 0, s_sd = 1, r_mu = 0, r_sd = 1, sample = False):
        """_summary_

        Args:
            idx (2D, jax array): An edglist of ids.
            focal_individual_predictors (2D jax array): each column represent node characteristics.
            target_individual_predictors (2D jax array): each column represent node characteristics.
            s_mu (int, optional): Default mean prior for focal_effect, defaults to 0.
            s_sd (int, optional): Default sd prior for focal_effect, defaults to 1.
            r_mu (int, optional): Default mean prior for target_effect, defaults to 0.
            r_sd (int, optional): Default sd prior for target_effect, defaults to 1.

        Returns:
            _type_: terms, focal_effects, target_effects
        """

        sender_effects = dist.normal(s_mu, s_sd, shape=(N_var_sender,), sample = sample, name = 'sender_effects')
        receiver_effects =  dist.normal( r_mu, r_sd, shape= (N_var_receiver,), sample = sample, name = 'receiver_effects')
        terms = jnp.stack([
            sender_effects @ sender_predictors, 
            receiver_effects @  receiver_predictors], 
            axis = -1)

        return terms, sender_effects, receiver_effects
    
    @staticmethod 
    @jit
    def node_effects_to_dyadic_format(sr_effects):
        """Convert node effects to dyadic (edge list) format.

        Args:
            sr_effects (jax array): Array of node effects with shape [N_nodes, 2].
        Returns:
            jax array: Dyadic effects with shape [N_dyads, 2], where each row represents 
            a dyad (i, j) with sender effect i and receiver effect j.
        """
        ids = jnp.arange(0,sr_effects.shape[0])
        edgl_idx = Neteffect.vec_node_to_edgle(jnp.stack([ids, ids], axis = -1))
        #sender = sr_effects[edgl_idx[:,0],0] + sr_effects[edgl_idx[:,1],1]
        #receiver = sr_effects[edgl_idx[:,1],0] + sr_effects[edgl_idx[:,0],1]
        #return jnp.stack([sender, receiver], axis = 1)
        S_i = sr_effects[edgl_idx[:,0],0]
        S_j = sr_effects[edgl_idx[:,1],0]
        R_i = sr_effects[edgl_idx[:,0],1]
        R_j = sr_effects[edgl_idx[:,1],1]
        return jnp.stack([S_i + R_j, S_j + R_i ], axis = 1)

    @staticmethod 
    def sender_receiver(sender_predictors, receiver_predictors,  
                        #Fixed effect parameters
                        s_mu = 0, s_sd = 1, r_mu = 0, r_sd = 1, 
                        #Random effect parameters
                        sr_mu = 0, sr_sd = 1, sr_sigma_rate = 1, 
                        cholesky_dim = 2, cholesky_density = 2,
                        sample = False, diag = False ):
        """Compute sender-receiver effects combining both fixed and random effects.

        Args:
            sender_predictors (jax array): Predictors for focal individuals.
            receiver_predictors (jax array): Predictors for target individuals.
            s_mu (float, optional): Mean for focal effects. Defaults to 0.
            s_sd (float, optional): SD for focal effects. Defaults to 1.
            r_mu (float, optional): Mean for target effects. Defaults to 0.
            r_sd (float, optional): SD for target effects. Defaults to 1.
            sr_mu (float, optional): Mean for random effects. Defaults to 0.
            sr_sd (float, optional): SD for random effects. Defaults to 1.
            sr_sigma_rate (float, optional): Rate parameter for random effects. Defaults to 1.
            cholesky_dim (int, optional): Dimension for Cholesky decomposition. Defaults to 2.
            cholesky_density (int, optional): Density parameter for Cholesky. Defaults to 2.
            sample (bool, optional): Whether to sample from distributions. Defaults to False.
            diag (bool, optional): Whether to print diagnostic information. Defaults to False.

        Returns:
            jax array: Combined dyadic effects.
        """        
        if sender_predictors is None and receiver_predictors is None:
            raise ValueError("At least one of sender_predictors or receiver_predictors must be provided.")

        N_var_sender = sender_predictors.shape[0]
        N_id = sender_predictors.shape[1]         

        N_var_receiver = receiver_predictors.shape[0]


        sr_ff, focal_effects, target_effects = Neteffect.nodes_terms(
            sender_predictors, receiver_predictors,
            N_var_sender = N_var_sender,N_var_receiver=N_var_receiver,
            s_mu = s_mu, s_sd = s_sd, r_mu = r_mu, r_sd = r_sd, sample = sample )
        sr_rf, sr_raw, sr_sigma, sr_L = Neteffect.nodes_random_effects(N_id, sr_mu = sr_mu, sr_sd = sr_sd, sr_sigma_rate = sr_sigma_rate, cholesky_dim = cholesky_dim, cholesky_density = cholesky_density,  sample = sample, diag = diag ) # shape = N_id
        sr_to_dyads = Neteffect.node_effects_to_dyadic_format(sr_ff + sr_rf) # sr_ff and sr_rf are nodal values that need to be converted to dyadic values
        return sr_to_dyads

    # dyadic effects ------------------------------------------
    @staticmethod 
    @jit
    def prepare_dyadic_effect(dyadic_effect_mat):
        """Prepare dyadic effect matrix for processing.

        Args:
            dyadic_effect_mat (jax array): Dyadic effect matrix to process.

        Returns:
            jax array: Processed dyadic effects in edge list format.
        """        
        if dyadic_effect_mat.ndim == 2:
            return Neteffect.mat_to_edgl(dyadic_effect_mat)
        elif dyadic_effect_mat.ndim == 3:
            return jax.vmap(Neteffect.mat_to_edgl, in_axes=2, out_axes=2)(dyadic_effect_mat)

    @staticmethod 
    def dyadic_random_effects(N_dyads, dr_mu = 0, dr_sd = 1, dr_sigma = 1, cholesky_dim = 2, cholesky_density = 2, sample = False, diag = False):
        """Generate random effects for dyadic models.

        Args:
            N_dyads (int): Number of dyads.
            dr_mu (float, optional): Mean for random effects. Defaults to 0.
            dr_sd (float, optional): SD for random effects. Defaults to 1.
            dr_sigma (float, optional): Sigma parameter for random effects. Defaults to 1.
            cholesky_dim (int, optional): Dimension for Cholesky decomposition. Defaults to 2.
            cholesky_density (int, optional): Density parameter for Cholesky. Defaults to 2.
            sample (bool, optional): Whether to sample from distributions. Defaults to False.
            diag (bool, optional): Whether to print diagnostic information. Defaults to False.

        Returns:
            tuple: Contains random effects, raw effects, sigma, and Cholesky decomposition matrix.
        """
        dr_raw =  dist.normal(dr_mu, dr_sd, shape=(2,N_dyads), name = 'dr_raw', sample = sample)
        dr_sigma = dist.exponential(dr_sigma, shape=(1,), name = 'dr_sigma', sample = sample )
        dr_L = dist.lkj_cholesky(cholesky_dim, cholesky_density, name = 'dr_L', sample = sample)
        dr_rf = deterministic('dr_rf', (((dr_L @ dr_raw).T * jnp.repeat(dr_sigma, 2))))
        if diag :
            print("dr_raw--------------------------------------------------------------------------------")
            print(dr_raw)
            print("dr_sigma--------------------------------------------------------------------------------")
            print(dr_sigma)
            print("dr_L--------------------------------------------------------------------------------")
            print(dr_L)
            print("rf--------------------------------------------------------------------------------")
            print(dr_rf)
        return dr_rf, dr_raw, dr_sigma, dr_L # we return everything to get posterior distributions for each parameters

    @staticmethod 
    def dyadic_terms(dyadic_predictors, d_m = 0, d_sd = 1, sample = False):
        """Calculate fixed effects for dyadic terms.

        Args:
            dyadic_predictors (jax array): Predictors for dyadic terms.
            d_m (float, optional): Mean for dyad effects. Defaults to 0.
            d_sd (float, optional): SD for dyad effects. Defaults to 1.
            sample (bool, optional): Whether to sample from distributions. Defaults to False.
            diag (bool, optional): Whether to print diagnostic information. Defaults to False.

        Returns:
            tuple: Contains fixed effects and dyadic predictors.
        """        
  
        
        if dyadic_predictors.ndim == 2:
            dyad_effects = dist.normal(d_m, d_sd, name= 'dyad_effects', shape = (1,), sample = sample)
            dr_ff = dyad_effects * dyadic_predictors

        elif dyadic_predictors.ndim == 3:
            dyad_effects = dist.normal(d_m, d_sd, name= 'dyad_effects', shape = (dyadic_predictors.shape[2],), sample = sample)
            dr_ff = jnp.tensordot(dyadic_predictors, dyad_effects, axes=[2, 0])
            
        return dr_ff, dyad_effects

    @staticmethod 
    def dyadic_effect(dyadic_predictors = None, shape = None, d_m = 0, d_sd = 1, # Fixed effect arguments
                     dr_mu = 0, dr_sd = 1, dr_sigma = 1, cholesky_dim = 2, cholesky_density = 2,
                     sample = False):
        """Compute dyadic effects combining both fixed and random components.
        
        Args:
            dyadic_predictors (jax array, optional): Predictors for dyadic effects.
            shape (int, optional): Shape parameter if predictors are not provided.
            d_m (float, optional): Mean for fixed effects. Defaults to 0.
            d_sd (float, optional): SD for fixed effects. Defaults to 1.
            dr_mu (float, optional): Mean for random effects. Defaults to 0.
            dr_sd (float, optional): SD for random effects. Defaults to 1.
            dr_sigma (float, optional): Sigma parameter for random effects. Defaults to 1.
            cholesky_dim (int, optional): Dimension for Cholesky decomposition. Defaults to 2.
            cholesky_density (int, optional): Density parameter for Cholesky. Defaults to 2.
            sample (bool, optional): Whether to sample from distributions. Defaults to False.
            
        Returns:
            jax array: Combined dyadic effects.
        """                     
        if dyadic_predictors is None and shape is None:
            print('Error: Argument shape must be defined if argument dyadic_predictors is not define')
            return 'Argument shape must be defined if argument dyadic_predictors is not define'
        if dyadic_predictors is not None :
            dr_ff, dyad_effects = Neteffect.dyadic_terms(dyadic_predictors, d_m = d_m, d_sd = d_sd, sample = sample)
            dr_rf, dr_raw, dr_sigma, dr_L =  Neteffect.dyadic_random_effects(dr_ff.shape[0], dr_mu = dr_mu, dr_sd = dr_sd, dr_sigma = dr_sigma, 
            cholesky_dim = cholesky_dim, cholesky_density = cholesky_density, sample = sample)
            return dr_ff + dr_rf
        else:
            dr_rf, dr_raw, dr_sigma, dr_L =  Neteffect.dyadic_random_effects(shape, dr_mu = dr_mu, dr_sd = dr_sd, dr_sigma = dr_sigma, 
            cholesky_dim = cholesky_dim, cholesky_density = cholesky_density, sample = sample)
        return  dr_rf
  
    @staticmethod 
    def block_model_prior(N_grp, 
                          b_ij_mean = 0.01, b_ij_sd = 1, 
                          b_ii_mean = 0.1, b_ii_sd = 1,
                          name_b_ij = 'b_ij', name_b_ii = 'b_ii', sample = False):
        """Build block model prior matrix for within and between group links probabilities

        Args:
            N_grp (int): Number of groups to build
            b_ij_mean (float, optional): mean prior for between groups. Defaults to 0.01.
            b_ij_sd (float, optional): sd prior for between groups. Defaults to 2.5.
            b_ii_mean (float, optional): mean prior for within groups. Defaults to 0.01.
            b_ii_sd (float, optional): sd prior for between groups. Defaults to 2.5.

        Returns:
            _type_: _description_
        """
        N_dyads = int(((N_grp*(N_grp-1))/2))
        b_ij = dist.normal(Neteffect.logit(b_ij_mean/jnp.sqrt(N_grp*0.5 + N_grp*0.5)), b_ij_sd, shape=(N_dyads, 2), name = name_b_ij, sample = sample) # transfers more likely within groups
        b_ii = dist.normal(Neteffect.logit(b_ii_mean/jnp.sqrt(N_grp)), b_ii_sd, shape=(N_grp, ), name = name_b_ii, sample = sample) # transfers less likely between groups
        b = Neteffect.edgl_to_mat(b_ij, N_grp)
        b = b.at[jnp.diag_indices_from(b)].set(b_ii)
        return b, b_ij, b_ii

    @staticmethod 
    @jit
    def block_prior_to_edglelist(v, b):
        """Convert block vector id group belonging to edgelist of i->j group values

        Args:
            v (1D array):  Vector of id group belonging
            b (2D array): Matrix of block model prior matrix (squared)

        Returns:
            _type_: 1D array representing the probability of links from i-> j 
        """

        v = Neteffect.vec_node_to_edgle(jnp.stack([v, v], axis= 1)).astype(int)

        return jnp.stack([b[v[:,0],v[:,1]], b[v[:,1],v[:,0]]], axis = 1)

    @staticmethod 
    def block_model(grp, N_grp, b_ij_mean = 0.01, b_ij_sd = 1, b_ii_mean = 0.1, b_ii_sd = 1, sample = False):
        """Generate block model model matrix.

        Args:
            grp (array): Array of group belonging
            N_grp (int): Number of groups to build
            b_ij_mean (float, optional): _description_. Defaults to 0.01.
            b_ij_sd (float, optional): _description_. Defaults to 2.5.
            b_ii_mean (float, optional): _description_. Defaults to 0.1.
            b_ii_sd (float, optional): _description_. Defaults to 2.5.
            name_b_ij (str, optional): _description_. Defaults to 'b_ij'.
            name_b_ii (str, optional): _description_. Defaults to 'b_ii'.
            sample (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        # Get grp name from user. This seems to slower down the code operations, but from user perspective it is more convenient.....
        frame = inspect.currentframe()
        frame = inspect.getouterframes(frame)[1]
        string = inspect.getframeinfo(frame[0]).code_context[0].strip()
        name = string[string.find('(') + 1:-1].split(',')[0]
        name_b_ij = 'b_ij_' + str(name)
        name_b_ii = 'b_ii_' + str(name) 

        b, b_ij, b_ii = Neteffect.block_model_prior(N_grp, 
                         b_ij_mean = b_ij_mean, b_ij_sd = b_ij_sd, 
                         b_ii_mean = b_ii_mean, b_ii_sd = b_ii_sd,
                         name_b_ij = name_b_ij, name_b_ii = name_b_ii, sample = sample)
        edgl_block = Neteffect.block_prior_to_edglelist(grp, b)

        return edgl_block


    @staticmethod
    def block_model2(group, N_group, N_by_group, b_ij_sd = 2.5, sample = False, name = ''): 
        mu_ij = Neteffect.block_build_mu_ij(group, N_by_group, N_group)
        b = dist.normal(Neteffect.logit(mu_ij), b_ij_sd, sample = sample, name = f'b_{name}')
        return Neteffect.block_prior_to_edglelist(group,b)

    @partial(jax.jit, static_argnums=(2,))
    def block_build_mu_ij(group, N_by_group, N_group):
        # N_group is now a static value known at compile time.
        base_rate = jnp.tile(0.01, (N_group, N_group))
        base_rate = base_rate.at[jnp.diag_indices_from(base_rate)].set(0.1)
        mu_ij = base_rate / jnp.sqrt(jnp.outer(N_by_group, N_by_group))
        return mu_ij