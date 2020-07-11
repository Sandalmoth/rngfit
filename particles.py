import numpy as np


PARTICLE_COUNT = 512
H_MEAN = 29
H_STD = 5
E_MEAN = 0.04
E_STD = 0.01

PREDICT_SIGMAS = (1e-0, 1e-1, 1e-3)
H_OU_SPRING = 0.01
RIR_SIGMA = 0.5


def make_particles(m_guess, m_std):
    """
    Setup particle filter for a new exercise
    """
    particles = np.random.normal(size=(PARTICLE_COUNT, 6))
    means = (0, m_guess, H_MEAN, E_MEAN)
    sigmas = (0, m_std, H_STD, E_STD)
    for i in range(6):
        particles[:, i] = means[i] + sigmas[i]*particles[:, i]
    particles[:, 1:] = np.clip(particles[:, 1:], a_min=1.e-3, a_max=None)
    return particles


def predict(particles, dt, sigmas=PREDICT_SIGMAS):
    """
    Predict particle positions dt into the future
    """
    particles[:, 0] += np.random.normal(0, sigmas[0], particles.shape[0])*dt
    particles[:, 1] += particles[:, 0]*dt
    particles[:, 2] += np.random.normal(0, sigmas[1], particles.shape[0])*dt - H_OU_SPRING*dt*(particles[:, 2] - H_MEAN)
    particles[:, 3] += np.random.normal(0, sigmas[2], particles.shape[0])*dt
    particles[:, 1:] = np.clip(particles[:, 3:], a_min=1.e-3, a_max=None)


def update(particles, weights, work, rir_sigma=RIR_SIGMA):
    for i, particle in enumerate(particles):
        predict_rir(*particle[1:], work)
        # rir_diff_first = work['est_rir'].to_numpy()[0] - \
        #                  work['rir'].to_numpy()[0] - 0.5
        # rir_diff_last = work['est_rir'].to_numpy()[-1] - \
        #                 work['rir'].to_numpy()[-1] - 0.5
        # weights[i] *= scipy.stats.norm(rir_diff_first, rir_sigma).pdf(0)
        # weights[i] *= scipy.stats.norm(rir_diff_last, rir_sigma).pdf(0)
        for j in range(len(work)):
            if np.isnan(work['rir']):
                continue
            rir_diff = work['est_rir'].to_numpy()[j] - \
                       work['rir'].to_numpy()[j] - 0.5
            weights[i] *= scipy.stats.norm(rir_diff, rir_sigma).pdf(0)
        # weights[i] *= scipy.stats.norm(particle[4] - H_MEAN, H_STD).pdf(0)
        # weights[i] *= scipy.stats.norm(particle[5] - E_MEAN, E_STD).pdf(0)

    weights += 1.e-300
    weights /= sum(weights)


def estimate(particles, weights):
    x = particles[:, 1:]
    mean = np.average(x, weights=weights, axis=0)
    sigma = np.average((x - mean)**2, weights=weights, axis=0)**(1/2)
    return mean, sigma

def neff(weights):
    return 1. / np.sum(np.square(weights))

def resample_from_index(particles, weights, indexes):
    particles[:] = particles[indexes]
    weights.resize(len(particles))
    weights.fill (1.0 / len(weights))
