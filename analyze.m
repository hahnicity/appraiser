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


function lambda = determine_best_lambda(training_set, cv_set, y_train, y_cv)
    lambda_vals = [1 2 4 10 40 100 300 500 800];
    j_train = [];
    j_cv = [];
    for lambda = lambda_vals
        theta = zeros(size(training_set)(2), 1);
        [theta, j_history] = perform_gradient_descent(training_set, y_train, theta, .1, lambda, 1000);
        j_cv(length(j_cv) + 1) = compute_cost(cv_set, y_cv, theta);
        j_train(length(j_train) + 1) = j_history(length(j_history));
    end
    [_, idx] = min(j_cv - j_train);
    lambda = lambda_vals(idx);
end


function main()
    data = load("appraiser/home-data.csv");
    x = data(:, 1:size(data)(2) - 1);
    y = data(:, size(data)(2));
    m = length(y);
    training_set_length = ceil(m * .6);
    if (mod(length(x) - training_set_length, 2) == 1)
        cv_set_length = ceil((m - training_set_length) / 2);
    else
        cv_set_length = (m - training_set_length) / 2;
    end
    x_normed = normalize_x(x);
    x = [ones(m, 1), x_normed];
    training_set = x(1:training_set_length, :);
    cv_set = x(training_set_length:training_set_length + cv_set_length, :);
    test_set = x(training_set_length + cv_set_length:m, :);
    lambda = determine_best_lambda(training_set, ...
                                   cv_set, ...
                                   y(1:training_set_length), ...
                                   y(training_set_length:training_set_length + cv_set_length));
    theta = zeros(size(x)(2), 1);
    [theta, _] = perform_gradient_descent(training_set, y(1:training_set_length), theta, .1, lambda, 10000);
    predictions = (test_set * theta)';
    idx = [1:length(predictions)];
    plot(idx, y(training_set_length + cv_set_length:m)', "color", "red");
    hold on;
    plot(idx, predictions, "color", "blue");
    xlabel("House index")
    ylabel("Price")
    legend("Predicted Prices", "Actual Prices")
    axis([1 length(idx)]);
    print -dpng results.png
    pause;
end


main
