function j = compute_cost(x, y, theta)
    m = length(y);
    predictions = x * theta;
    j = (1 / (2 * m)) * sum((predictions - y) .^ 2);
end


function x_normed = normalize_x(x)
    x_normed = [];
    for i = 1:size(x, 2)
        x_normed(:, i) = (x(:, i) - mean(x(:, i))) / std(x(:, i));
    end
end


function [theta, j_history] = perform_gradient_descent(x, y, theta, alpha, lambda, iterations)
    m = length(y);
    j_history = zeros(iterations, 1);
    for iter = 1:iterations
        tmp = [];
        for j = 1:columns(x)
            k = ((alpha * (1 / m)) * sum((x * theta - y)' * x(:,j)));
            if (j > 1)
                tmp(j) = theta(j) * (1 - alpha * (lambda / m)) - k;
            else
                tmp(j) = theta(j) - k;
            end
        end
        for j = 1:columns(x)
            theta(j) = tmp(j);
        end
        j_history(iter) = compute_cost(x, y, theta);
    end
end


function main()
    data = load("appraiser/home-data.csv");
    x = data(:, 1:size(data)(2) - 1);
    y = data(:, size(data)(2));
    m = length(y);
    x_normed = normalize_x(x);
    x = [ones(m, 1), x_normed];
    theta = zeros(size(x)(2), 1);
    [theta, j_history] = perform_gradient_descent(x, y, theta, .1, 0, 500);
    j_history
    theta
end


main
